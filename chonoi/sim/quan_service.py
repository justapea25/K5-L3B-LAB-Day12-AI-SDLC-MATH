"""Quán lát 4 (@minhthu27) — bếp, bưng, phục vụ, tiền, boa, uy tín. Lát này giữ luôn `quan.py`.

Theo schema khách trong docs/contracts/customer.md (bản của @viethoang126, theo PRD-0 D/E/F):
`dish_id`, `order_tick`, `state` (waiting|eating), `patience_ticks_left`, `eat_ticks_left`,
`order_status` (reserved|assigned|unfulfillable|served), `reserved`, `base_price`, `tip`.

Thứ tự một bước (quan.py gọi):  1 `tick_service` (bếp nấu, khách ăn)  ->  2 `interact`  ->
3 `settle` (khách ăn xong trả tiền, rời bàn)  ->  hết ca: `settle(closing=True)`.
Phần kiên nhẫn / rời đi / khách mới là của lát 3 (KHÔNG giảm `eat_ticks_left` ở lát 3, đã làm ở đây).

`stock` là tồn vật lý gồm cả phần giữ chỗ: khi bếp nhận đơn, nguyên liệu bị trừ khỏi kho và `reserved` về {}.
Món ở bếp (`stoves[].dish`) và trên tay (`hand`) đều là payload `{order_id, dish_id, base_price}`.
Khách rời vì kiên nhẫn / closing thì `quan_customers.remove_customer` tự bỏ món của đơn đó.
"""

import math

from .. import inventory as inv
from ..ids import id_key
from .quan_customers import remove_customer, reserve_for

TICK = 60


def _clamp_rep(sim, v):
    return max(sim.t["reputation_min"], min(sim.t["reputation_max"], v))


# --- bước 1: bếp nấu, khách ăn ----------------------------------------------------------
def tick_service(sim, events):
    for s in sim.stoves:  # theo id (sim.stoves đã sắp)
        if s["state"] == "cooking":
            s["cook_ticks_left"] = max(0, s["cook_ticks_left"] - 1)
            if s["cook_ticks_left"] == 0:
                s["state"], s["ready_ticks"] = "ready", 0
                events.append(("dish_ready", {"stove_id": s["id"], "order_id": s["dish"]["order_id"],
                                          "dish_id": s["dish"]["dish_id"]}))
        elif s["state"] == "ready":
            s["ready_ticks"] += 1
            if sim.burn_ticks is not None and s["ready_ticks"] > sim.burn_ticks:  # đúng burn_ticks vẫn bưng được
                _burn(sim, s, events)
    for c in sim.customers:
        if c["state"] == "eating":
            c["eat_ticks_left"] = max(0, c["eat_ticks_left"] - 1)


def _burn(sim, s, events):
    """Mở rộng burn: bỏ món, nguyên liệu mất, bếp rảnh ngay; thử giữ lại ngay cho đơn
    (đủ -> reserved, thiếu -> unfulfillable, khách tiếp tục chờ tới hết kiên nhẫn)."""
    dish = s["dish"]
    _reset_stove(s)
    c = next((c for c in sim.customers if c["id"] == dish["order_id"]), None)
    status = None
    if c is not None:
        got = reserve_for(sim, c["dish_id"], skip=c)
        c["reserved"], c["order_status"] = (got, "reserved") if got is not None else ([], "unfulfillable")
        status = c["order_status"]
    events.append(("dish_burnt", {"stove_id": s["id"], "order_id": dish["order_id"], "dish_id": dish["dish_id"],
                                  "order_status": status}))


def _reset_stove(s):
    s["state"], s["dish"], s["cook_ticks_left"], s["ready_ticks"] = "idle", None, 0, 0


# --- bước 3: trả tiền ---------------------------------------------------------------------
def settle(sim, events, closing=False):
    """Theo id bàn: khách ăn xong (eat_ticks_left == 0) trả tiền rồi rời bàn. Hết ca: mọi khách đang ăn trả ngay."""
    rank = {tb["id"]: i for i, tb in enumerate(sim.tables)}
    eating = [c for c in sim.customers if c["state"] == "eating" and (closing or c["eat_ticks_left"] <= 0)]
    eating.sort(key=lambda c: rank.get(c["table_id"], 0))
    for c in eating:
        total = c["base_price"] + c["tip"]
        if c["tip"] > 0:
            sim.reputation = _clamp_rep(sim, sim.reputation + sim.t["tip_reputation"])
        sim.money += total
        sim.earned += total
        sim.shift_earned += total
        events.append(("paid", {"order_id": c["id"], "table_id": c["table_id"], "base_price": c["base_price"],
                                "tip": c["tip"], "amount": total,
                                "reason": "closing" if closing else "eaten"}))
        remove_customer(sim, c)


# --- bước 2: interact ----------------------------------------------------------------------
def interact(sim, events):
    """Tối đa MỘT interact/bước: đối tượng trong interact_radius theo (khoảng cách, bếp trước bàn, id)."""
    r = sim.t["interact_radius"]
    cands = [(math.dist(sim.pos, o["pos"]), kind, id_key(o["id"]), o)
             for kind, objs in ((0, sim.stoves), (1, sim.tables)) for o in objs]
    cands = sorted((c for c in cands if c[0] <= r), key=lambda c: c[:3])
    if not cands:
        return
    kind, obj = cands[0][1], cands[0][3]
    (_use_stove if kind == 0 else _use_table)(sim, obj, events)


def _use_stove(sim, s, events):
    if s["state"] == "ready":
        if sim.hand is None:  # carry_limit = 1
            sim.hand = s["dish"]
            events.append(("dish_picked", {"stove_id": s["id"], "order_id": s["dish"]["order_id"],
                                           "dish_id": s["dish"]["dish_id"]}))
            _reset_stove(s)
    elif s["state"] == "idle":
        _start_cooking(sim, s, events)


def _start_cooking(sim, s, events):
    """Nhận đơn `reserved` CŨ NHẤT (order_tick rồi id bàn). v1.2: tiêu đúng các id đang giữ,
    chốt base_price = floor(giá niêm yết × trung bình fresh / 100)."""
    for c in sorted(sim.customers, key=lambda c: (c["order_tick"], id_key(c["table_id"]))):
        if c["state"] != "waiting" or c["order_status"] != "reserved" or not c["reserved"]:
            continue
        ids = set(c["reserved"])
        used = [it for it in sim.stock if it["id"] in ids]
        sim.stock = [it for it in sim.stock if it["id"] not in ids]
        price = inv.priced(sim.menu[c["dish_id"]]["price"], used)
        c["reserved"], c["order_status"] = [], "assigned"
        s.update(state="cooking", ready_ticks=0,
                 dish={"order_id": c["id"], "dish_id": c["dish_id"], "base_price": price},
                 cook_ticks_left=int(round(sim.menu[c["dish_id"]]["cook_s"] * TICK)))
        items = [inv.item_out(it) for it in sorted(used, key=lambda it: (it["kind"], id_key(it["id"])))]
        events.append(("cook_started", {"stove_id": s["id"], "order_id": c["id"], "dish_id": c["dish_id"],
                                        "items": items}))
        return


def _use_table(sim, tb, events):
    """Bưng món: khách ngồi bàn này phải là chủ đơn của món trên tay."""
    h = sim.hand
    if not isinstance(h, dict):
        return
    for c in sim.customers:
        if c["table_id"] == tb["id"] and c["state"] == "waiting" and c["id"] == h.get("order_id"):
            tip = 0
            if c["patience_ticks_left"] >= sim.t["tip_min_patience_ratio"] * sim.t["patience_s"] * TICK:
                tip = int(math.floor(h["base_price"] * sim.t["tip_rate"]))
            c.update(state="eating", order_status="served", eat_ticks_left=int(round(sim.t["eat_s"] * TICK)),
                     base_price=h["base_price"], tip=tip)
            events.append(("served", {"order_id": c["id"], "table_id": tb["id"], "dish_id": h["dish_id"],
                                      "patience_ticks_left": c["patience_ticks_left"],
                                      "base_price": h["base_price"], "tip": tip}))
            sim.hand = None
            return
