"""Benchmark có render (Test Contract v1.3): python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json

Cảnh đo: buổi sáng lõi (độ tươi, cá bơi, Cá Sấu Năm Chèo, hiệu ứng mặc định), Út Sen đứng yên ở bến, seed 42.
Mỗi khung: mô phỏng theo bước cố định 60 tick/s (theo thời gian thực) rồi VẼ cảnh vào framebuffer RGB 1280×720
(nền nước theo độ sâu, nút hái, đàn cá, Cá Sấu, người chơi, thanh HUD). Vẽ bằng phần mềm nên chạy được trên máy
không có màn hình. Làm nóng 3 s rồi đo `--duration` giây.

Xuất {avg_fps, p1_low_fps, frames, measured_s, load_ms}:
  avg_fps = frames / measured_s; p1_low_fps = 1 / trung bình thời gian của max(1, ceil(1% × frames)) khung chậm nhất;
  load_ms = từ lúc khởi chạy tới khung đầu tiên của cảnh đo.
"""

import argparse
import json
import math
import sys
import time

T_START = time.perf_counter()

from .contract import load_contract  # noqa: E402
from .ids import IdAllocator  # noqa: E402
from .inputs import InputState  # noqa: E402
from .rng import Streams  # noqa: E402
from .sim.gather import GatherSim  # noqa: E402

W, H = 1280, 720
WARMUP_S = 3.0
IDLE = InputState((0.0, 0.0), {}, set())
COLORS = {"ca_loc": (124, 154, 82), "ca_linh": (214, 230, 242), "ca_keo": (217, 160, 102),
          "bong_dien_dien": (242, 194, 48), "bong_sung": (232, 121, 156), "keo_neo": (143, 207, 107)}


class Frame:
    """Framebuffer RGB phẳng; vẽ hình chữ nhật bằng gán lát theo hàng."""

    def __init__(self):
        self.buf = bytearray(W * H * 3)
        # nền: dải màu nước theo độ sâu, dựng sẵn một lần
        rows = []
        for y in range(H):
            k = y / H
            rows.append(bytes((int(20 + 10 * k), int(70 - 40 * k), int(110 - 60 * k))) * W)
        self.bg = b"".join(rows)

    def clear(self):
        self.buf[:] = self.bg

    def rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(W, int(x + w)), min(H, int(y + h))
        if x1 <= x0 or y1 <= y0:
            return
        line = bytes(rgb) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.buf[i:i + len(line)] = line


def render(fb, sim):
    bx, bd = sim.t["bounds"]["x"][1], sim.t["bounds"]["d"][1]
    sx, sy = W / bx, (H - 80) / bd

    def at(p):
        return p[0] * sx, 40 + p[1] * sy

    fb.clear()
    fb.rect(0, 40 + 0.5 * sy - 2, W, 3, (180, 220, 240))  # mặt nước
    for n in sim.nodes:
        x, y = at(n["pos"])
        fb.rect(x - 8, y - 14, 16, 14, COLORS[n["kind"]] if n["regrow_ticks"] == 0 else (90, 90, 90))
    for f in sim.fish:
        x, y = at(f["pos"])
        fb.rect(x - 10, y - 5, 20, 10, COLORS[f["kind"]])
    for m in sim.monsters:
        x, y = at(m["pos"])
        fb.rect(x - 22, y - 8, 44, 16, (60, 120, 60) if m["state"] != "chase" else (170, 60, 200))
    x, y = at(sim.pos)
    fb.rect(x - 7, y - 12, 14, 24, (255, 213, 128))
    # HUD: oxy, Máu, giỏ (thanh độ tươi)
    fb.rect(10, 10, 200 * sim.oxygen_ticks / sim.oxygen_max, 12, (79, 195, 247))
    for i in range(sim.hp):
        fb.rect(220 + i * 18, 10, 14, 12, (229, 57, 53))
    for i, it in enumerate(sim.hold):
        fb.rect(10 + i * 26, H - 32, 22, 22, COLORS[it["kind"]])


def bench(seed, duration, tuning):
    sim = GatherSim(tuning, {}, Streams(seed), IdAllocator())  # đứng yên ở bến (start_pos = dock_pos)
    fb = Frame()
    step_s = 1.0 / tuning["tick_hz"]
    times, load_ms = [], None
    t_prev = time.perf_counter()
    acc = 0.0
    measure_from = t_prev + WARMUP_S
    end = measure_from + duration
    measuring = False
    while True:
        now = time.perf_counter()
        dt, t_prev = now - t_prev, now
        acc += dt
        while acc >= step_s and not sim.done:
            sim.step(IDLE)
            acc -= step_s
        render(fb, sim)
        done_at = time.perf_counter()
        if load_ms is None:
            load_ms = round((done_at - T_START) * 1000)
        if measuring:
            times.append(done_at - now)
        elif done_at >= measure_from:
            measuring, t_measure = True, done_at
        if done_at >= end:
            break
    measured = round(time.perf_counter() - t_measure, 3)  # avg_fps tính đúng trên số đã xuất
    frames = len(times)
    k = max(1, math.ceil(0.01 * frames))
    slow = sorted(times, reverse=True)[:k]
    return {"avg_fps": round(frames / measured, 2), "p1_low_fps": round(1.0 / (sum(slow) / k), 2),
            "frames": frames, "measured_s": measured, "load_ms": load_ms}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.bench")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--duration", type=float, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.duration <= 0:
        sys.stderr.write("--duration phải > 0\n")
        return 2
    out = bench(a.seed, a.duration, load_contract()["tuning"])
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f)
        f.write("\n")
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
