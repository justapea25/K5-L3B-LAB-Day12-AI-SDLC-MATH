"""Soak headless (Test Contract v1.3): python3 -m chonoi.soak --seed 7 --days 10 --out soak.json

Chạy N Ngày trong MỘT tiến trình bằng bot tất định. Mỗi Ngày đi qua gather -> quan -> shop; kế hoạch D1–D5
lặp ở Ngày 6–10. Tiền, earned, uy tín, cấp nâng cấp, số Ngày và id cá thể tiếp tục xuyên suốt.
Xuất {days, days_completed, crashes, results[{day, earned, reputation, score}], duration_s} (results lấy lúc Shop đóng).
Không ghi bảng xếp hạng. duration_s là thời gian thực, bỏ qua khi so tính lặp.
"""

import argparse
import json
import math
import sys
import time

from .contract import load_contract
from .day import DaySession
from .errors import BadInput
from .inputs import InputState


class Bot:
    """Bot tất định: sáng bơi ra hái N1 rồi về bến; tối đứng ở bếp B1 bấm tương tác; Shop mua oxy rồi đóng."""

    def __init__(self):
        self.t = 0

    def input(self, sess):
        phase, pt = sess.sim.phase, sess.phase_tick
        self.t += 1
        pulse = self.t % 2 == 0  # nhấn/nhả xen kẽ để mỗi lần nhấn là một cạnh lên
        if phase == "gather":
            if pt < 150:
                return InputState((1.0, 0.0), {}, {"interact"} if pulse and pt > 140 else set())
            if pt < 300:
                return InputState((-1.0, 0.0), {}, set())
            return InputState((0.0, 0.0), {}, {"interact"} if pulse else set())
        if phase == "quan":
            return InputState((0.0, 0.0), {}, {"interact"} if pulse else set())
        buy = "oxygen" if pt == 1 else None
        return InputState((0.0, 0.0), {}, {"shop_done"} if pt >= 2 and pulse else set(), buy)


def soak(seed, days, tuning):
    sess = DaySession(tuning, {}, seed, days)
    bot = Bot()
    results, crashes = [], 0
    limit = days * 22_200 * 2
    while not sess.done and sess.tick < limit:
        day, phase = sess.day, sess.sim.phase
        try:
            rows = sess.step(bot.input(sess))
        except Exception as e:  # noqa: BLE001 — soak đếm sự cố thay vì dừng
            crashes += 1
            sys.stderr.write(f"crash Ngày {day} ({phase}): {e!r}\n")
            break
        for r in rows:
            if r["name"] == "shop_end":
                mult = tuning["score"]["reputation_multiplier"]
                results.append({"day": r["day"], "earned": sess.earned, "reputation": sess.reputation,
                                "score": sess.earned + mult * math.floor(sess.reputation)})
    return {"days": days, "days_completed": sess.days_completed, "crashes": crashes, "results": results}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.soak")
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args(argv)
    if a.days < 1:
        sys.stderr.write("--days phải >= 1\n")
        return 2
    try:
        tuning = load_contract()["tuning"]
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    t0 = time.perf_counter()
    out = soak(a.seed, a.days, tuning)
    out["duration_s"] = round(time.perf_counter() - t0, 3)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0 if out["crashes"] == 0 and out["days_completed"] == a.days else 1


if __name__ == "__main__":
    sys.exit(main())
