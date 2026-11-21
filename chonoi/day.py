"""Chế độ `day` (Test Contract v1.1): vòng Ngày gather -> quan -> shop, lặp tới --days Ngày.

Đổi pha (mục 4.5): day_start -> day_plan -> phase_start(gather). Sau gather_end dựng quán và phát
phase_start(quan) CÙNG tick (kể cả khi ngất). Sau quan_end dựng Shop và phát phase_start(shop) cùng tick.
Pha mới chỉ chạy gameplay từ bước sau. Đóng Shop thì tăng days_completed, kết thúc hoặc dựng Ngày kế ngay tick đó;
chỉ khi dựng Ngày mới mới sao cấp đã mua sang active_upgrades.

Xuyên Ngày giữ: money, earned, reputation, upgrades. Mỗi Ngày: oxy/Máu đầy theo cấp đang áp dụng, giỏ làm mới,
kho dư bị bỏ sau Shop. DayIntro/EveningIntro/DayResult là màn UI, không chiếm tick trong headless.
"""

import copy
import math

from . import inventory as inv
from .ids import IdAllocator
from .rng import Streams
from .runner import PauseMixin, common_snapshot
from .shop import ShopSim
from .sim.gather import GatherSim
from .sim.quan import QuanSim


class DaySession(PauseMixin):
    mode = "day"

    def __init__(self, tuning, scenario, seed, days=1, pantry=False):
        self.tuning = tuning
        self.days_total = days
        # chỉ cửa sổ chơi --demo: tối nào Má Tư cũng mua thêm đủ nguyên liệu theo kế hoạch (headless luôn tắt)
        self.pantry = pantry
        self.streams = Streams(seed)  # một bộ RNG cho cả lượt: các Ngày không lặp lại nhau
        d = scenario.get("day", {})
        self.gather_tpl = scenario.get("gather", {})
        self.quan_tpl = scenario.get("quan", {})
        self.money = d.get("money", 0)
        self.earned = d.get("earned", 0)
        self.reputation = d.get("reputation", tuning["quan"]["reputation_initial"])
        self.upgrades = dict(d.get("upgrades", {}))
        self.active_upgrades = dict(self.upgrades)
        self.plans = {p["day"]: p for p in copy.deepcopy(tuning["day_plan"])}
        for p in d.get("day_plan", []):
            self.plans[p["day"]] = p
        self.item_ids = IdAllocator()  # I1, I2... tăng xuyên pha và Ngày
        self.hold_tpl = inv.validate_item_list(self.gather_tpl.get("hold", []), "gather.hold")
        self.day = 1
        self.days_completed = 0
        self.tick = 0
        self.sim_tick = 0
        self.phase_tick = 0
        self.done = False
        self.reason = None
        self.sim = None
        self._pending = []
        self._start_day(self._pending)

    # --- dựng pha -------------------------------------------------------------
    def _plan(self):
        """Kế hoạch D1–D5; soak chạy quá 5 Ngày thì lặp lại (Ngày 6 = D1...)."""
        n = len(self.plans)
        return self.plans[(self.day - 1) % n + 1]

    def _start_day(self, out):
        out.append(("gather", "day_start", {}))
        p = self._plan()
        out.append(("gather", "day_plan", {"dishes": p["dishes"], "ingredients": p["ingredients"]}))
        t = copy.deepcopy(self.tuning)
        for uid, field, key in (("oxygen", "oxygen_max_s", "oxygen_max_s"), ("hp", "hp_max", "hp_max")):
            lv = self.active_upgrades.get(uid, 0)
            if lv:
                t["gather"][field] = t["shop"]["upgrades"][uid][lv - 1][key]
        sc = dict(self.gather_tpl)
        if self.day == 1:  # Ngày đầu giữ nguyên id trong mẫu; các Ngày kế cấp id mới theo thứ tự mảng
            hold = [dict(it) for it in self.hold_tpl]
        else:
            hold = [{"id": self.item_ids.new("I"), "kind": it["kind"], "units": it["units"]} for it in self.hold_tpl]
        net_lv = self.active_upgrades.get("net", 0)
        net = t["shop"]["upgrades"]["net"][net_lv - 1] if net_lv else None
        self.sim = GatherSim(t, sc, self.streams, IdAllocator(), day=self.day, item_ids=self.item_ids, hold=hold,
                             net=net)
        self._sync_into_sim()
        self.phase_tick = 0
        out.append(("gather", "phase_start", {}))

    def _start_quan(self, items, out):
        if self.pantry:  # demo: thêm hàng chợ tươi 100, id mới, sau hàng mang về
            for kind, n in sorted(self._plan()["ingredients"].items()):
                items = items + [inv.new_item(self.item_ids, kind, 100) for _ in range(n)]
        t = copy.deepcopy(self.tuning)
        dishes = self._plan()["dishes"]
        t["menu"] = {k: v for k, v in t["menu"].items() if k in dishes}  # lọc menu theo kế hoạch trước
        sc = dict(self.quan_tpl, reputation=self.reputation)
        self.sim = QuanSim(t, sc, self.streams, IdAllocator(), inventory=items)
        self._sync_into_sim()
        self.phase_tick = 0
        out.append(("quan", "phase_start", {}))

    def _start_shop(self, stock, out):
        self.sim = ShopSim(self.tuning, self.money, self.earned, self.reputation, self.upgrades, stock)
        self.phase_tick = 0
        out.append(("shop", "phase_start", {}))

    def _sync_into_sim(self):
        self.sim.money, self.sim.earned = self.money, self.earned
        self.sim.reputation = self.reputation

    def _sync_from_sim(self):
        self.money, self.earned, self.reputation = self.sim.money, self.sim.earned, self.sim.reputation

    # --- giao diện như runner.Session ------------------------------------------------
    def initial_events(self):
        rows = [self._row(0, ph, name, data, self.day) for ph, name, data in self._pending]
        self._pending = []
        return rows

    def _row(self, tick, phase, name, data, day):
        return {"type": "event", "tick": tick, "phase": phase, "day": day, "name": name, "data": data}

    def step(self, inp):
        run_it, pause_ev = self._pause_gate(inp)
        phase, day = self.sim.phase, self.day
        events = [(phase, n, d) for n, d in pause_ev]
        after = []
        if run_it:
            events += [(phase, n, d) for n, d in self.sim.step(inp)]
            self.sim_tick += 1
            self.phase_tick += 1
            if self.sim.done:
                after = self._advance()
        self.tick += 1
        rows = [self._row(self.tick, ph, n, d, day) for ph, n, d in events]
        rows += [self._row(self.tick, ph, n, d, dd) for ph, n, d, dd in after]
        return rows

    def _advance(self):
        """Pha hiện tại vừa kết thúc: dựng pha kế trong cùng tick. Trả [(phase, name, data, day)]."""
        out = []
        sim = self.sim
        self._sync_from_sim()
        if sim.phase == "gather":
            self._start_quan([dict(it) for it in sim.hold], out)  # bàn giao trong bộ nhớ, không hao thêm
        elif sim.phase == "quan":
            self._start_shop(sim.stock, out)
        else:  # shop đóng
            self.days_completed += 1
            if self.days_completed >= self.days_total:
                self.done, self.reason = True, "days_complete"
                return []
            self.day += 1
            self.active_upgrades = dict(self.upgrades)
            self._start_day(out)
        return [(ph, n, d, self.day) for ph, n, d in out]

    def _state(self):
        return "finished" if self.done else ("paused" if self.paused else "playing")

    def snapshot(self):
        s = common_snapshot(self.sim, self.tick, self.sim_tick, self.phase_tick, self.tuning, self._state(),
                            mode="day")
        s.update({"day": self.day, "day_plan": self._plan(), "upgrades": dict(self.upgrades),
                  "active_upgrades": dict(self.active_upgrades)})
        s.update(self.sim.snapshot())
        return s

    def end_row(self):
        if not self.done:
            self._sync_from_sim()
        mult = self.tuning["score"]["reputation_multiplier"]
        return {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": "day",
                "state": "finished" if self.done else "playing",
                "reason": self.reason if self.done else "tick_limit", "days_completed": self.days_completed,
                "money": self.money, "earned": self.earned, "reputation": self.reputation,
                "score": self.earned + mult * math.floor(self.reputation)}

    def write_inventory_if_done(self, inventory_out):
        """day tự bàn giao kho trong bộ nhớ; không ghi file."""
