"""Đọc game.contract.json và kiểm dải hợp lệ của tuning (Test Contract v1.1)."""

import json
import os

from .errors import BadInput
from .inventory import FISH_KINDS, NODE_KINDS

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "game.contract.json")


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _between(name, v, lo, hi):
    if not _num(v) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải trong [{lo}, {hi}], đang là {v!r}")


def load_contract(path=DEFAULT_PATH) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            c = json.load(f)
    except (OSError, ValueError) as e:
        raise BadInput(f"không đọc được {path}: {e}")
    exts = c.get("extensions", [])
    if not isinstance(exts, list) or any(e not in EXTENSIONS for e in exts) or len(set(exts)) != len(exts):
        raise BadInput(f"extensions phải là mảng mã không trùng thuộc {sorted(EXTENSIONS)}")
    validate_tuning(c.get("tuning"), exts)
    c["tuning"]["extensions"] = list(exts)  # để luật đọc qua tuning: "burn" in tuning["extensions"]
    return c


EXTENSIONS = {"weapon", "net", "snake", "burn", "vendor", "ca_ho", "current", "reservations", "settings"}
CORE_UPGRADES = ("oxygen", "hp")


def enabled(tuning, code) -> bool:
    """Mở rộng `code` có được khai trong manifest không (tắt thì luật lõi giữ nguyên)."""
    return code in tuning.get("extensions", ())


def _int_between(name, v, lo, hi):
    if isinstance(v, bool) or not isinstance(v, int) or not (lo <= v <= hi):
        raise BadInput(f"tuning.{name} phải là số nguyên trong [{lo}, {hi}], đang là {v!r}")


def _pos_in(name, pos, bounds, keys):
    if (not isinstance(pos, list) or len(pos) != 2 or not all(_num(c) for c in pos)):
        raise BadInput(f"tuning.{name} phải là [số, số]")
    for c, k in zip(pos, keys):
        lo, hi = bounds[k]
        if not (lo <= c <= hi):
            raise BadInput(f"tuning.{name} nằm ngoài vùng {k} ∈ [{lo}, {hi}]")


def _bounds(name, b, keys):
    if not isinstance(b, dict) or set(b) != set(keys):
        raise BadInput(f"tuning.{name}.bounds phải có đúng khóa {list(keys)}")
    for k in keys:
        v = b[k]
        if not (isinstance(v, list) and len(v) == 2 and all(_num(c) for c in v) and v[0] == 0 and v[1] > 0):
            raise BadInput(f"tuning.{name}.bounds.{k} phải là [0, số dương]")


def _validate_gather(g):
    """Dải hợp lệ P1 theo PRD mục 13.2."""
    _between("gather.duration_s", g.get("duration_s"), 60, 600)
    _bounds("gather", g.get("bounds"), ("x", "d"))
    b = g["bounds"]
    _between("gather.dock_radius", g.get("dock_radius"), 0.5, 5)
    _between("gather.interact_radius", g.get("interact_radius"), 0.5, 5)
    _between("gather.catch_radius", g.get("catch_radius"), 0.5, 5)
    _between("gather.swim_speed", g.get("swim_speed"), 1, 10)
    _between("gather.catch_cooldown_s", g.get("catch_cooldown_s"), 0, 10)
    _between("gather.oxygen_max_s", g.get("oxygen_max_s"), 10, 120)
    _int_between("gather.ramp_max_ticks", g.get("ramp_max_ticks"), 0, 6)
    _int_between("gather.hold_capacity", g.get("hold_capacity"), 4, 30)
    _int_between("gather.hp_max", g.get("hp_max"), 1, 99)
    _int_between("gather.oxygen_refill_per_tick", g.get("oxygen_refill_per_tick"), 1, 10_000)
    _int_between("gather.choke_interval_ticks", g.get("choke_interval_ticks"), 1, 10_000)
    _int_between("gather.node_yield", g.get("node_yield"), 1, 12)
    _between("gather.regrow_s", g.get("regrow_s"), 0.1, 600)
    _between("gather.surface_depth", g.get("surface_depth"), 0, 5)
    _pos_in("gather.dock_pos", g.get("dock_pos"), b, ("x", "d"))
    _pos_in("gather.start_pos", g.get("start_pos"), b, ("x", "d"))
    if not _num(g.get("start_heading_deg")):
        raise BadInput("tuning.gather.start_heading_deg phải là số")
    fy = g.get("fish_yield")
    if not isinstance(fy, dict) or set(fy) != set(FISH_KINDS):
        raise BadInput(f"tuning.gather.fish_yield phải có đúng {FISH_KINDS}")
    for k, v in fy.items():
        _int_between(f"gather.fish_yield.{k}", v, 1, g["hold_capacity"])
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise BadInput("tuning.gather.nodes phải là mảng không rỗng")
    seen, kinds = set(), set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or n["id"] in seen:
            raise BadInput("tuning.gather.nodes: mỗi nút cần id duy nhất")
        seen.add(n["id"])
        if n.get("kind") not in NODE_KINDS:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: kind phải thuộc {NODE_KINDS}")
        kinds.add(n["kind"])
        _pos_in(f"gather.nodes.{n['id']}.pos", n.get("pos"), b, ("x", "d"))
        if n["pos"][1] != 0:
            raise BadInput(f"tuning.gather.nodes.{n['id']}: nút hái nằm ở mặt nước (d = 0)")
    if kinds != set(NODE_KINDS):
        raise BadInput(f"tuning.gather.nodes phải có ít nhất một nút mỗi loại {NODE_KINDS}")
    _int_between("gather.fish_initial", g.get("fish_initial"), 0, 30)
    _int_between("gather.fish_max", g.get("fish_max"), g["fish_initial"], 30)
    _between("gather.fish_speed", g.get("fish_speed"), 0, 10)
    _int_between("gather.fish_turn_ticks", g.get("fish_turn_ticks"), 1, 100_000)
    _int_between("gather.fish_spawn_ticks", g.get("fish_spawn_ticks"), 1, 100_000)
    _between("gather.fish_spawn_clearance", g.get("fish_spawn_clearance"), 0, 100)
    for key in ("fish_depths", "fish_spawn_depths", "fish_weights"):
        if not isinstance(g.get(key), dict) or set(g[key]) != set(FISH_KINDS):
            raise BadInput(f"tuning.gather.{key} phải có đúng {FISH_KINDS}")
    if not isinstance(g.get("fish_spawn_x"), list) or not g["fish_spawn_x"]:
        raise BadInput("tuning.gather.fish_spawn_x phải là mảng không rỗng")
    m = g.get("monsters")
    if not isinstance(m, dict) or not isinstance(m.get("species"), dict) or not isinstance(m.get("spawns"), list):
        raise BadInput("tuning.gather.monsters phải có species và spawns")
    for sp in m["spawns"]:
        if sp.get("kind") not in m["species"]:
            raise BadInput(f"tuning.gather.monsters.spawns.{sp.get('id')}: kind không có trong species")
    _int_between("gather.monsters.invuln_ticks", m.get("invuln_ticks"), 0, 100_000)
    _between("gather.monsters.loss_ratio", m.get("loss_ratio"), 0, 1)


def _validate_day(t):
    menu = t["menu"]
    plans = t.get("day_plan")
    if not isinstance(plans, list) or [p.get("day") for p in plans] != list(range(1, len(plans) + 1)):
        raise BadInput("tuning.day_plan phải là mảng theo Ngày 1..N")
    for p in plans:
        need = {}
        for dish, n in p.get("dishes", {}).items():
            if dish not in menu:
                raise BadInput(f"tuning.day_plan.{p['day']}: món lạ {dish}")
            _int_between(f"day_plan.{p['day']}.dishes.{dish}", n, 1, 99)
            for k, v in menu[dish]["recipe"].items():
                need[k] = need.get(k, 0) + v * n
        if p.get("ingredients") != need:
            raise BadInput(f"tuning.day_plan.{p['day']}: ingredients khác tổng công thức × số suất")
    shop = t.get("shop")
    if not isinstance(shop, dict) or not isinstance(shop.get("upgrades"), dict):
        raise BadInput("tuning.shop phải có max_ticks và upgrades")
    _int_between("shop.max_ticks", shop.get("max_ticks"), 1, 100_000)
    for uid, levels in shop["upgrades"].items():
        if [lv.get("level") for lv in levels] != list(range(1, len(levels) + 1)):
            raise BadInput(f"tuning.shop.upgrades.{uid}: level phải là 1..N")
        for lv in levels:
            _int_between(f"shop.upgrades.{uid}.price", lv.get("price"), 1, 1_000_000)


def _validate_skills(sk):
    """Khối `skills` (sáng tạo của nhóm, tắt mặc định) là tùy chọn; có thì phải hợp lệ."""
    if sk is None:
        return
    if not isinstance(sk, dict) or not isinstance(sk.get("enabled"), bool):
        raise BadInput("tuning.skills phải là object có enabled (boolean)")
    _between("skills.net_radius", sk.get("net_radius"), 0.5, 20)
    _int_between("skills.net_max_schools", sk.get("net_max_schools"), 1, 12)
    _int_between("skills.net_extra_oxygen_ticks", sk.get("net_extra_oxygen_ticks"), 0, 10)
    _between("skills.sprint_speed_mult", sk.get("sprint_speed_mult"), 1, 3)
    _int_between("skills.sprint_extra_oxygen_ticks", sk.get("sprint_extra_oxygen_ticks"), 0, 10)


def validate_tuning(t, exts=()):
    if not isinstance(t, dict):
        raise BadInput("thiếu khối tuning")
    g, q, menu = t.get("gather"), t.get("quan"), t.get("menu")
    if not isinstance(g, dict) or not isinstance(q, dict) or not isinstance(menu, dict):
        raise BadInput("tuning phải có gather, quan, menu")
    _validate_gather(g)
    _validate_day(t)
    _validate_skills(t.get("skills"))
    fr = t.get("freshness")
    if not isinstance(fr, dict) or set(fr) != {"initial", "gather_decay_per_s", "quan_decay_per_s", "spoiled_below"}:
        raise BadInput("tuning.freshness phải có initial, gather_decay_per_s, quan_decay_per_s, spoiled_below")
    _between("freshness.initial", fr["initial"], 0, 100)
    _between("freshness.spoiled_below", fr["spoiled_below"], 0, 100)
    _between("freshness.gather_decay_per_s", fr["gather_decay_per_s"], 0, 100)
    _between("freshness.quan_decay_per_s", fr["quan_decay_per_s"], 0, 100)
    # Quán: dải hợp lệ P1 (PRD mục 13.2)
    _between("quan.duration_s", q.get("duration_s"), 60, 600)
    _bounds("quan", q.get("bounds"), ("x", "z"))
    _between("quan.patience_s", q.get("patience_s"), 20, 180)
    _between("quan.walk_speed", q.get("walk_speed"), 1, 10)
    _between("quan.interact_radius", q.get("interact_radius"), 0.5, 5)
    _int_between("quan.ramp_max_ticks", q.get("ramp_max_ticks", 6), 0, 6)
    _between("quan.eat_s", q.get("eat_s"), 0.1, 600)
    _between("quan.customer_interval_s", q.get("customer_interval_s"), 0.1, 600)
    _int_between("quan.first_customer_tick", q.get("first_customer_tick"), 1, int(q["duration_s"] * 60) - 1)
    if not (_num(q.get("tip_rate")) and q["tip_rate"] > 0 and _num(q.get("left_reputation_delta"))
            and q["left_reputation_delta"] < 0):
        raise BadInput("tip_rate phải > 0 và left_reputation_delta phải < 0")
    ratio = q.get("tip_min_patience_ratio")
    if not (_num(ratio) and 0 < ratio <= 1):
        raise BadInput("quan.tip_min_patience_ratio phải thuộc (0, 1]")
    if not (_num(q.get("tip_reputation")) and q["tip_reputation"] > 0):
        raise BadInput("quan.tip_reputation phải > 0")
    if "burn" in exts:
        _between("quan.burn_s", q.get("burn_s"), 0.1, 600)
    elif q.get("burn_s") is not None:
        raise BadInput("burn_s phải là null khi chưa bật mở rộng burn")
    if "net" in exts:
        levels = t.get("shop", {}).get("upgrades", {}).get("net")
        if not isinstance(levels, list) or not levels:
            raise BadInput("bật net cần shop.upgrades.net[] {level, price, catch_radius, max_schools}")
        for lv in levels:
            _between("shop.upgrades.net.catch_radius", lv.get("catch_radius"), 0.5, 20)
            _int_between("shop.upgrades.net.max_schools", lv.get("max_schools"), 1, 12)
    # TODO(nhóm): bổ sung kiểm các khóa còn lại nếu muốn chặt hơn (bếp/bàn, uy tín, ...).
    for dish_id, d in menu.items():
        price, cook = d.get("price"), d.get("cook_s")
        if isinstance(price, bool) or not isinstance(price, int) or price <= 0 or not _num(cook) or cook <= 0:
            raise BadInput(f"menu.{dish_id}: price (nguyên) và cook_s phải > 0")
