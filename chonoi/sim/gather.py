"""Buổi sáng — Lặn & Hái (`gather`). KHUNG: bơi, chặn mép, đồng hồ, cập bến, xuất kho.

Mặt cắt dòng sông nhìn NGANG: vị trí `[x, d]` (x sang phải, `d` độ sâu hướng xuống, d = 0 là mặt nước).
`move = [x, d]`: thành phần thứ hai DƯƠNG = bơi xuống. Hướng mặt là góc từ +x, dương = xuống.

Đã làm sẵn để smoke test chạy được: bơi + tăng/giảm tốc, chặn mép (d không âm), đồng hồ và hết giờ,
cập bến (`interact` trong vùng bến -> `gather_end` reason `docked`), xuất kho, snapshot đầy đủ trường gather.

Phân chia lát:
  - Lát 1 (file này): oxy, ngạt, Máu, ngất, dive/surface, giỏ LIFO (`_add_to_hold`). ĐÃ XONG.
  - Lát 2 (`gather_harvest.py`): hái nút, bắt cá.
  - v1.1: cá bơi/sinh (`gather_fish.py`), Cá Sấu (`gather_monsters.py`).
  File này đã nối sẵn lời gọi theo thứ tự mục 4.5 Test Contract v1.1; các lát KHÔNG cần sửa file này.
Các tính năng của phase sau chưa nằm trong khung này.
"""

import math

from ..ids import sort_by_id
from .. import inventory as inv
from . import gather_fish as fish
from . import gather_harvest as harvest
from . import gather_monsters as monsters
from . import gather_skills as skills
from .ramp import ramp_velocity

TICK = 60.0
AXES = ("x", "d")


class GatherSim:
    mode = "gather"
    phase = "gather"

    def __init__(self, tuning, scenario, streams, ids, day=1, item_ids=None, hold=None, net=None):
        t = tuning["gather"]
        self.t = t
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.heading = float(p.get("heading_deg", t["start_heading_deg"]))
        self.oxygen_max = int(round(t["oxygen_max_s"] * TICK))
        self.oxygen_ticks = p.get("oxygen_ticks", self.oxygen_max)
        self.hp = p.get("hp", t["hp_max"])
        self.zero_oxy_ticks = p.get("zero_oxy_ticks", 0)
        self.invuln_ticks = p.get("invuln_ticks", 0)
        self.catch_cd_ticks = p.get("catch_cd_ticks", 0)
        # v1.2: giỏ là mảng cá thể {id, kind, units}, thứ tự vào giỏ (cuối = mới nhất, LIFO)
        self.item_ids = item_ids if item_ids is not None else ids
        self.fresh_cfg = tuning["freshness"]
        self.decay_units = inv.units_per_tick(self.fresh_cfg["gather_decay_per_s"])
        if hold is not None:  # day dựng sẵn (id mới cho các Ngày kế)
            self.hold = hold
        else:
            self.hold = inv.validate_item_list(scenario.get("hold", []), "gather.hold")
        for it in self.hold:
            self.item_ids.reserve(it["id"])
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        # nút và đàn cá: scenario THAY THẾ danh sách mặc định; random_fish=false tắt cá mặc định
        src_nodes = scenario["nodes"] if "nodes" in scenario else t["nodes"]
        self.nodes = [{"id": n["id"], "kind": n["kind"], "pos": [float(c) for c in n["pos"]],
                       "regrow_ticks": n.get("regrow_ticks", 0)} for n in src_nodes]
        self.phase_tick = 0  # số bước gameplay đã chạy trong buổi (lịch sinh cá dùng)
        self.day = day  # chế độ day truyền vào; gather độc lập = bố trí Ngày 1
        # mở rộng net: {level, price, catch_radius, max_schools} của cấp đang áp dụng; None = luật lõi (cấp 0)
        self.net = net if "net" in tuning.get("extensions", ()) else None
        # kỹ năng thêm (F lưới, G tăng tốc): None = tắt, luật lõi
        self.skills = skills.build(tuning)
        self.net_on = False
        self.sprint_on = False
        for n in self.nodes:
            ids.reserve(n["id"])
        # đàn cá: scenario.fish THAY đàn ban đầu; random_fish=false tắt cá mặc định, bơi và sinh
        self.random_fish = scenario.get("random_fish", True)
        self.fish = [{"id": f["id"], "kind": f["kind"], "pos": [float(c) for c in f["pos"]],
                      "heading_deg": f.get("heading_deg", 0), "age_ticks": f.get("age_ticks", 0)}
                     for f in scenario.get("fish", [])]
        for f in self.fish:
            ids.reserve(f["id"])
        if "fish" not in scenario and self.random_fish:
            fish.spawn_initial(self)
        self.monsters = monsters.build(self, scenario)
        self.money = 0
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.done = False
        self.reason = None

    # --- giao diện cho runner -------------------------------------------------
    def inventory_items(self) -> dict:
        return [inv.item_out(it) for it in inv.by_id(self.hold)]

    def snapshot(self) -> dict:
        snap = {
            "player": {"pos": self.pos, "vel": self.vel, "heading_deg": self.heading,
                       "oxygen_ticks": self.oxygen_ticks, "oxygen_max_ticks": self.oxygen_max,
                       "hp": self.hp, "hp_max": self.t["hp_max"], "zero_oxy_ticks": self.zero_oxy_ticks,
                       "invuln_ticks": self.invuln_ticks, "catch_cd_ticks": self.catch_cd_ticks,
                       "at_surface": self._at_surface()},
            "hold": [inv.item_out(it) for it in self.hold], "hold_count": len(self.hold),
            "hold_capacity": self.t["hold_capacity"],
            "nodes": [{"id": n["id"], "pos": n["pos"], "kind": n["kind"],
                       "ready": n["regrow_ticks"] == 0, "regrow_ticks": n["regrow_ticks"]}
                      for n in sort_by_id(self.nodes)],
            "fish": [{"id": f["id"], "pos": f["pos"], "kind": f["kind"], "heading_deg": f["heading_deg"],
                      "age_ticks": f["age_ticks"]} for f in sort_by_id(self.fish)],
            "monsters": monsters.snapshot(self),
        }
        return skills.annotate(self, snap)

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        events = []
        skills.begin_step(self, inp)
        # 1. đồng hồ và hàng có sẵn: giảm bộ đếm, nút mọc lại
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.invuln_ticks = max(0, self.invuln_ticks - 1)
        self.catch_cd_ticks = max(0, self.catch_cd_ticks - 1)
        for n in sort_by_id(self.nodes):
            if n["regrow_ticks"] > 0:
                n["regrow_ticks"] -= 1
                if n["regrow_ticks"] == 0:
                    events.append(("node_regrown", {"node_id": n["id"]}))
        # độ tươi hàng có sẵn trong giỏ (hàng mới nhặt bắt đầu hao từ bước sau)
        inv.decay(self.hold, self.decay_units, self.fresh_cfg["spoiled_below"], "hold", events)
        # 2. bơi + oxy + ngạt (ngất -> dừng bước)
        was_surface = self._at_surface()
        self._move(inp)
        if self._zone_and_oxygen(was_surface, events):
            return events
        # 3. Cá Sấu theo id, tối đa một hit (ngất -> dừng bước)
        if monsters.update(self, events):
            return events
        # 4. interact: bến trước, rồi hái
        if inp.pressed("interact"):
            if self._in_dock():
                self._finish("docked", events)
                return events
            harvest.try_gather(self, events)
        # 5. bắt cá theo vị trí cá TRƯỚC khi cá bơi
        if inp.pressed("catch"):
            harvest.try_catch(self, events)
        # 6. hết giờ
        self.phase_tick += 1
        if self.time_left_ticks <= 0:
            self._finish("time", events)
            return events
        # 7. còn giờ: cá bơi rồi sinh thêm theo lịch
        if self.random_fish:
            fish.swim(self, events)
            fish.spawn_scheduled(self, events)
        return events

    # --- lát 1: oxy, ngạt, Máu, ngất, giỏ ----------------------------------------
    def _zone_and_oxygen(self, was_surface, events) -> bool:
        """Xét theo vị trí CUỐI bước. Trả True nếu buổi kết thúc vì ngất."""
        now_surface = self._at_surface()
        if was_surface and not now_surface:
            events.append(("dive", {"pos": list(self.pos)}))
        elif now_surface and not was_surface:
            events.append(("surface", {"pos": list(self.pos)}))

        if now_surface:
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + int(self.t["oxygen_refill_per_tick"]))
            self.zero_oxy_ticks = 0
            return False

        before = self.oxygen_ticks
        self.oxygen_ticks = max(0, self.oxygen_ticks - 1 - skills.extra_oxygen_drain(self))
        if before > 0 and self.oxygen_ticks == 0:
            events.append(("oxygen_empty", {"oxygen_ticks": self.oxygen_ticks}))
        if self.oxygen_ticks > 0:
            self.zero_oxy_ticks = 0
            return False

        self.zero_oxy_ticks += 1
        if self.zero_oxy_ticks < int(self.t["choke_interval_ticks"]):
            return False
        self.zero_oxy_ticks = 0
        self.hp = max(0, self.hp - 1)
        events.append(("choke", {"hp": self.hp}))
        if self.hp > 0:
            return False
        self._faint(events, "choke")
        return True

    def _faint(self, events, cause):
        """Máu về 0: mất toàn bộ giỏ, faint rồi gather_end(fainted). cause: "choke" hoặc "monster"."""
        lost = [inv.item_out(it) for it in reversed(self.hold)]  # bỏ phần còn lại theo LIFO
        events.append(("faint", {"cause": cause, "hp": 0, "lost": lost}))
        self.hold = []
        self._finish("fainted", events)

    def _add_to_hold(self, kind, n, events, source=None) -> bool:
        """Thêm n món `kind` vào giỏ (cuối mảng = mới nhất, LIFO).
        Không đủ chỗ cho cả n -> không thêm gì, phát hold_full {**source, required, free}, trả False.
        source: {"action": "catch", "fish_id": ...} hoặc {"action": "gather", "node_id": ...}."""
        cap = int(self.t["hold_capacity"])
        if len(self.hold) + n > cap:
            events.append(("hold_full", {**(source or {}), "required": n, "free": cap - len(self.hold)}))
            return False
        for _ in range(n):  # fresh = initial lúc bắt/hái, id I1, I2... theo thứ tự vào giỏ
            self.hold.append(inv.new_item(self.item_ids, kind, self.fresh_cfg["initial"]))
        return True

    # --- tiện ích ---------------------------------------------------------------
    def _at_surface(self) -> bool:
        return self.pos[1] <= self.t["surface_depth"]

    def _in_dock(self) -> bool:
        return math.dist(self.pos, self.t["dock_pos"]) <= self.t["dock_radius"]

    def _finish(self, reason, events):
        self.done = True
        self.reason = reason
        events.append(("gather_end", {"reason": reason, "inventory": {"items": self.inventory_items()}}))

    def _move(self, inp):
        speed = self.t["swim_speed"] * skills.speed_factor(self)
        mx, md = inp.move
        self.vel = ramp_velocity(self, (mx * speed, md * speed), int(self.t["ramp_max_ticks"]))
        if (mx, md) != (0.0, 0.0):
            self.heading = math.degrees(math.atan2(md, mx)) % 360
        b = self.t["bounds"]
        for i, axis in enumerate(AXES):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i] = lo
                self.vel[i] = max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i] = hi
                self.vel[i] = min(0.0, self.vel[i])
