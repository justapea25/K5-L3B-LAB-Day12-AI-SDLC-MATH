"""So game.contract.json với số chuẩn Test Contract v1.3.

Số chuẩn lõi lấy từ TICKET-02 mục 1–2, 4.1 (v1.1); thêm `tuning.freshness` (TICKET-03, v1.2) và
`bench_cmd`/`soak_cmd` ở gốc (TICKET-04, v1.3). Mở rộng đã khai trong `extensions` thì kiểm khóa đi kèm.

Chạy: python3 .agents/skills/check-contract/check_contract.py [đường-dẫn-contract]
Mã thoát 0 khi khớp, 1 khi còn chỗ thiếu/sai (in từng dòng).
"""

import json
import sys

VERSION = "1.3"

# đường dẫn khóa (tách bằng ".") → giá trị chuẩn
EXPECTED = {
    "contract_version": VERSION,
    "tuning.tick_hz": 60,
    # Độ tươi (v1.2)
    "tuning.freshness": {"initial": 100, "gather_decay_per_s": 0.5, "quan_decay_per_s": 0.25, "spoiled_below": 30},
    # Buổi sáng
    "tuning.gather.duration_s": 180,
    "tuning.gather.bounds": {"x": [0, 100], "d": [0, 30]},
    "tuning.gather.dock_pos": [2, 0],
    "tuning.gather.dock_radius": 3,
    "tuning.gather.start_pos": [2, 0],
    "tuning.gather.start_heading_deg": 0,
    "tuning.gather.swim_speed": 4.0,
    "tuning.gather.ramp_max_ticks": 6,
    "tuning.gather.surface_depth": 0.5,
    "tuning.gather.oxygen_max_s": 30,
    "tuning.gather.oxygen_refill_per_tick": 6,
    "tuning.gather.choke_interval_ticks": 60,
    "tuning.gather.hp_max": 3,
    "tuning.gather.hold_capacity": 12,
    "tuning.gather.interact_radius": 2.0,
    "tuning.gather.node_yield": 1,
    "tuning.gather.regrow_s": 20,
    "tuning.gather.catch_radius": 2.0,
    "tuning.gather.catch_cooldown_s": 0.5,
    "tuning.gather.fish_yield": {"ca_linh": 3, "ca_loc": 1, "ca_keo": 2},
    "tuning.gather.fish_initial": 8,
    "tuning.gather.fish_speed": 1.5,
    "tuning.gather.fish_turn_ticks": 120,
    "tuning.gather.fish_max": 12,
    "tuning.gather.fish_spawn_ticks": 360,
    "tuning.gather.fish_spawn_clearance": 1,
    "tuning.gather.fish_x": [4, 96],
    "tuning.gather.fish_depths": {"ca_linh": [3, 12], "ca_loc": [8, 20], "ca_keo": [22, 28]},
    "tuning.gather.fish_spawn_x": [15, 30, 45, 60, 75, 90],
    "tuning.gather.fish_spawn_depths": {"ca_linh": [5, 10], "ca_loc": [10, 16], "ca_keo": [24, 27]},
    "tuning.gather.monsters.invuln_ticks": 90,
    "tuning.gather.monsters.loss_ratio": 0.5,
    "tuning.gather.monsters.species.ca_sau.patrol_speed": 1.0,
    "tuning.gather.monsters.species.ca_sau.chase_speed": 3.0,
    "tuning.gather.monsters.species.ca_sau.detect_radius": 10,
    "tuning.gather.monsters.species.ca_sau.exit_radius": 16,
    "tuning.gather.monsters.species.ca_sau.depths": [10, 30],
    "tuning.gather.monsters.species.ca_sau.hit_radius": 1.5,
    "tuning.gather.monsters.species.ca_sau.recoil_ticks": 60,
    # Buổi tối
    "tuning.quan.duration_s": 180,
    "tuning.quan.bounds": {"x": [0, 16], "z": [0, 10]},
    "tuning.quan.start_pos": [8, 5],
    "tuning.quan.walk_speed": 4.0,
    "tuning.quan.ramp_max_ticks": 6,
    "tuning.quan.interact_radius": 1.5,
    "tuning.quan.first_customer_tick": 120,
    "tuning.quan.customer_interval_s": 15,
    "tuning.quan.patience_s": 60,
    "tuning.quan.eat_s": 10,
    "tuning.quan.carry_limit": 1,
    "tuning.quan.tip_rate": 0.2,
    "tuning.quan.tip_min_patience_ratio": 0.5,
    "tuning.quan.tip_reputation": 0.2,
    "tuning.quan.left_reputation_delta": -0.5,
    "tuning.quan.reputation_initial": 3.0,
    "tuning.quan.reputation_min": 0,
    "tuning.quan.reputation_max": 5,
    "tuning.score.reputation_multiplier": 100,
    "tuning.shop.max_ticks": 600,
}

NODES = {"N1": ("bong_dien_dien", [12, 0]), "N2": ("bong_dien_dien", [28, 0]),
         "N3": ("bong_sung", [44, 0]), "N4": ("bong_sung", [60, 0]),
         "N5": ("keo_neo", [76, 0]), "N6": ("keo_neo", [90, 0])}
STOVES = {"B1": [2, 8], "B2": [5, 8]}
TABLES = {"T1": [9, 2], "T2": [13, 2], "T3": [9, 6], "T4": [13, 6]}
MENU = {
    "ca_loc_nuong_trui": ({"ca_loc": 1}, 6, 60),
    "goi_bong_sung": ({"bong_sung": 2}, 4, 40),
    "lau_ca_linh_dien_dien": ({"ca_linh": 3, "bong_dien_dien": 1}, 10, 120),
    "canh_chua_ca_loc": ({"ca_loc": 1, "bong_dien_dien": 1}, 8, 90),
    "ca_keo_nuong": ({"ca_keo": 2}, 6, 70),
    "lau_mam": ({"ca_linh": 2, "ca_keo": 1, "keo_neo": 1, "bong_dien_dien": 1}, 12, 200),
}
DAY_PLAN = {
    1: {"ca_loc_nuong_trui": 3, "goi_bong_sung": 3},
    2: {"ca_loc_nuong_trui": 2, "lau_ca_linh_dien_dien": 2},
    3: {"goi_bong_sung": 2, "canh_chua_ca_loc": 2, "ca_keo_nuong": 2},
    4: {"lau_mam": 1, "ca_loc_nuong_trui": 2, "goi_bong_sung": 1},
    5: {"lau_mam": 1, "lau_ca_linh_dien_dien": 1, "ca_loc_nuong_trui": 1},
}
UPGRADES = {
    "oxygen": [(1, 200, "oxygen_max_s", 45), (2, 400, "oxygen_max_s", 60)],
    "hp": [(1, 250, "hp_max", 4), (2, 500, "hp_max", 5)],
}
MONSTER_SPAWNS = {"M1": ("ca_sau", [60, 24], [[60, 24], [64, 24]], 1),
                  "M2": ("ca_sau", [85, 18], [[85, 18], [89, 18]], 3)}

_MISSING = object()


def get(c, path):
    cur = c
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return _MISSING
        cur = cur[part]
    return cur


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 1e-9
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def by_id(items):
    return {x.get("id"): x for x in items or [] if isinstance(x, dict)}


def check(c):
    errs = []
    for path, want in EXPECTED.items():
        got = get(c, path)
        if got is _MISSING:
            errs.append(f"thiếu {path} (chuẩn: {json.dumps(want)})")
        elif not same(got, want):
            errs.append(f"{path} = {json.dumps(got)}, chuẩn {json.dumps(want)}")
    # Đơn vị không ghi rõ trong TICKET-02: chỉ kiểm có mặt và tỷ lệ, không ép một cách viết.
    if get(c, "tuning.gather.monsters.species.ca_sau.recoil_dist") is _MISSING:
        errs.append("thiếu tuning.gather.monsters.species.ca_sau.recoil_dist (lùi 2/60 m mỗi bước, 60 bước = 2 m)")
    w = get(c, "tuning.gather.fish_weights")
    if not isinstance(w, dict) or set(w) != {"ca_linh", "ca_loc", "ca_keo"} or not all(isinstance(v, (int, float)) for v in w.values()):
        errs.append(f"tuning.gather.fish_weights phải có đủ 3 loài, đang là {w if w is not _MISSING else 'thiếu'}")
    else:
        total = sum(w.values())
        if total <= 0 or not same([w["ca_linh"] / total, w["ca_loc"] / total, w["ca_keo"] / total], [0.4, 0.3, 0.3]):
            errs.append(f"tuning.gather.fish_weights phải theo tỷ lệ linh 40%, lóc 30%, kèo 30%, đang là {w}")
    burn = get(c, "tuning.quan.burn_s")
    if burn is _MISSING:
        errs.append("thiếu tuning.quan.burn_s (lõi: null; mở rộng Cháy: 20)")

    # v1.3: lệnh benchmark và soak ở gốc
    for key in ("bench_cmd", "soak_cmd"):
        v = c.get(key)
        if not isinstance(v, str) or not v.strip():
            errs.append(f"thiếu {key} ở gốc (chuỗi lệnh khác rỗng, vd. \"python3 -m chonoi.{key[:-4]}\")")

    # Mở rộng đã khai thì phải có khóa đi kèm
    ext = c.get("extensions")
    if not isinstance(ext, list) or not all(isinstance(e, str) for e in ext):
        errs.append(f"extensions phải là mảng chuỗi, đang là {ext}")
        ext = []
    if "burn" in ext and not (isinstance(burn, (int, float)) and not isinstance(burn, bool) and burn > 0):
        errs.append(f"extensions có burn nhưng tuning.quan.burn_s = {burn if burn is not _MISSING else 'thiếu'} (chuẩn 20)")
    if "net" in ext:
        net = get(c, "tuning.shop.upgrades.net")
        if not isinstance(net, list) or not net:
            errs.append("extensions có net nhưng thiếu tuning.shop.upgrades.net")

    nodes = by_id(get(c, "tuning.gather.nodes") if get(c, "tuning.gather.nodes") is not _MISSING else [])
    for nid, (kind, pos) in NODES.items():
        n = nodes.get(nid)
        if not n or n.get("kind") != kind or not same(n.get("pos"), pos):
            errs.append(f"nút {nid} phải là {kind} tại {pos}, đang là {n}")

    spawns = by_id(get(c, "tuning.gather.monsters.spawns") if get(c, "tuning.gather.monsters.spawns") is not _MISSING else [])
    for mid, (kind, pos, wps, from_day) in MONSTER_SPAWNS.items():
        m = spawns.get(mid)
        if not m or m.get("kind") != kind or not same(m.get("pos"), pos) or not same(m.get("waypoints"), wps) or m.get("from_day") != from_day:
            errs.append(f"quái {mid} phải là {kind} pos {pos} waypoints {wps} from_day {from_day}, đang là {m}")

    for key, want in (("stoves", STOVES), ("tables", TABLES)):
        got = by_id(get(c, f"tuning.quan.{key}") if get(c, f"tuning.quan.{key}") is not _MISSING else [])
        if set(got) != set(want):
            errs.append(f"tuning.quan.{key} phải có đúng {sorted(want)}, đang có {sorted(got)}")
        for i, pos in want.items():
            if i in got and not same(got[i].get("pos"), pos):
                errs.append(f"{i} phải ở {pos}, đang ở {got[i].get('pos')}")

    menu = get(c, "tuning.menu")
    menu = menu if isinstance(menu, dict) else {}
    if set(menu) != set(MENU):
        errs.append(f"tuning.menu phải có đúng 6 món {sorted(MENU)}, đang có {sorted(menu)}")
    for dish, (recipe, cook, price) in MENU.items():
        d = menu.get(dish, {})
        if d and (not same(d.get("recipe"), recipe) or not same(d.get("cook_s"), cook) or d.get("price") != price):
            errs.append(f"món {dish} phải là recipe {recipe}, cook_s {cook}, price {price}; đang là {d}")

    plan = get(c, "tuning.day_plan")
    plan = {p.get("day"): p for p in plan} if isinstance(plan, list) else {}
    for day, dishes in DAY_PLAN.items():
        p = plan.get(day)
        ingredients = {}
        for dish, n in dishes.items():
            for k, q in MENU[dish][0].items():
                ingredients[k] = ingredients.get(k, 0) + q * n
        if not p or not same(p.get("dishes"), dishes) or not same(p.get("ingredients"), ingredients):
            errs.append(f"day_plan Ngày {day} phải là dishes {dishes}, ingredients {ingredients}; đang là {p}")

    for kind, levels in UPGRADES.items():
        got = get(c, f"tuning.shop.upgrades.{kind}")
        got = got if isinstance(got, list) else []
        want = [{"level": lv, "price": pr, field: val} for lv, pr, field, val in levels]
        if not same(got, want):
            errs.append(f"tuning.shop.upgrades.{kind} phải là {want}, đang là {got}")
    return errs


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    path = sys.argv[1] if len(sys.argv) > 1 else "game.contract.json"
    with open(path, encoding="utf-8") as f:
        c = json.load(f)
    errs = check(c)
    for e in errs:
        print("- " + e)
    print(f"{'KHỚP' if not errs else 'CHƯA KHỚP'} số chuẩn v{VERSION}: {len(errs)} chỗ cần sửa")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
