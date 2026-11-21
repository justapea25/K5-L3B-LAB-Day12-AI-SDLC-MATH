"""Vòng tick (Contract B, mô hình tick). KHUNG — thường không cần sửa.

Thứ tự ghi: snapshot tick 0 -> với mỗi bước: sự kiện (theo thứ tự xử lý) rồi snapshot (nếu tới lượt
hoặc buổi kết thúc) -> dòng 'end'. Mỗi tick tối đa một snapshot.

`Session` là API bước tick gọn dùng chung cho headless (`run`) và cửa sổ chơi trực tiếp (`chonoi.live`):
cả hai chạy CÙNG một lớp sim, không nhân đôi logic.
"""

import math

from .ids import IdAllocator
from .inputs import InputPlayer
from .inventory import write_inventory
from .jsonl import JsonlWriter
from .rng import Streams
from .sim.gather import GatherSim
from .sim.quan import QuanSim


def build_sim(mode, tuning, scenario, seed, inventory):
    streams, ids = Streams(seed), IdAllocator()
    if mode == "gather":
        return GatherSim(tuning, scenario, streams, ids)
    return QuanSim(tuning, scenario, streams, ids, inventory=inventory)


def common_snapshot(sim, tick, sim_tick, phase_tick, tuning, state, mode=None):
    mult = tuning["score"]["reputation_multiplier"]
    return {
        "type": "snapshot", "tick": tick, "sim_tick": sim_tick, "mode": mode or sim.mode, "phase": sim.phase,
        "phase_tick": phase_tick, "state": state, "time_left_ticks": sim.time_left_ticks,
        "money": sim.money, "earned": sim.earned, "reputation": sim.reputation,
        "score": sim.earned + mult * math.floor(sim.reputation),
    }


_common = common_snapshot  # tên cũ


class PauseMixin:
    """Pause (v1.1 mục 4.2): xét cạnh pause trước. Vào pause chỉ tăng tick ngoài và phát `paused`;
    còn pause thì bỏ qua cạnh hành động và buy; sim_tick, phase_tick, lịch và timer đứng yên.
    Cạnh pause tiếp theo phát `resumed` và chạy gameplay ngay trong bước đó."""

    paused = False

    def _pause_gate(self, inp):
        """Trả (chạy gameplay?, các event pause)."""
        if inp.pressed("pause"):
            self.paused = not self.paused
            return (not self.paused), [("paused" if self.paused else "resumed", {})]
        return (not self.paused), []


class Session(PauseMixin):
    """Một lượt chơi một mode (gather/quan): dựng sim, bước từng tick, lấy snapshot / dòng end."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None):
        self.mode = mode
        self.tuning = tuning
        self.sim = build_sim(mode, tuning, scenario, seed, inventory)
        self.tick = 0
        self.sim_tick = 0

    @property
    def done(self) -> bool:
        return self.sim.done

    def initial_events(self) -> list:
        return []

    def _state(self):
        return "finished" if self.sim.done else ("paused" if self.paused else "playing")

    def snapshot(self) -> dict:
        s = common_snapshot(self.sim, self.tick, self.sim_tick, self.sim_tick, self.tuning, self._state())
        s.update(self.sim.snapshot())
        return s

    def step(self, inp) -> list:
        """Chạy một bước với `inp` (chonoi.inputs.InputState); trả các dòng event (tick = k + 1)."""
        run_it, events = self._pause_gate(inp)
        if run_it:
            events += self.sim.step(inp)
            self.sim_tick += 1
        self.tick += 1
        return [{"type": "event", "tick": self.tick, "phase": self.sim.phase, "name": name, "data": data}
                for name, data in events]

    def end_row(self) -> dict:
        sim = self.sim
        score = common_snapshot(sim, self.tick, self.sim_tick, self.sim_tick, self.tuning, "")["score"]
        return {"type": "end", "ticks": self.tick, "sim_tick": self.sim_tick, "mode": sim.mode,
                "state": "finished" if sim.done else "playing",
                "reason": sim.reason if sim.done else "tick_limit",
                "money": sim.money, "earned": sim.earned, "reputation": sim.reputation, "score": score}

    def write_inventory_if_done(self, inventory_out):
        """File kho: ghi MỘT lần khi có gather_end; chưa kết thúc thì giữ nguyên file đích."""
        if self.mode == "gather" and self.sim.done and inventory_out:
            write_inventory(inventory_out, self.sim.inventory_items())


def make_session(mode, tuning, scenario, seed, inventory=None, days=1, pantry=False):
    if mode == "day":
        from .day import DaySession
        return DaySession(tuning, scenario, seed, days, pantry=pantry)
    return Session(mode, tuning, scenario, seed, inventory)


def run(mode, tuning, scenario, seed, frames, ticks, out_path, snapshot_every, inventory=None, inventory_out=None,
        days=1):
    sess = make_session(mode, tuning, scenario, seed, inventory, days)
    player = InputPlayer(frames)
    w = JsonlWriter(out_path)
    try:
        for row in sess.initial_events():  # day: day_start, day_plan, phase_start ở tick 0
            w.write(row)
        w.write(sess.snapshot())  # tick 0: sau khi dựng scenario, trước mọi input
        last_snapped = 0
        while sess.tick < ticks and not sess.done:
            inp = player.advance(sess.tick)  # bước k đọc input có tick == k
            rows = sess.step(inp)
            for row in rows:
                w.write(row)
            phase_changed = any(r["name"] == "phase_start" for r in rows)
            if sess.tick % snapshot_every == 0 or sess.done or phase_changed:
                w.write(sess.snapshot())
                last_snapped = sess.tick
        if last_snapped != sess.tick:
            w.write(sess.snapshot())
        w.write(sess.end_row())
    finally:
        w.close()
    sess.write_inventory_if_done(inventory_out)
    return sess.sim
