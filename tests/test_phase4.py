"""Phase 4 (v1.3): manifest khai bench_cmd/soak_cmd; bench.json và soak.json đúng cấu trúc."""

import json
import shlex
import subprocess
import unittest

from helpers import ROOT, Workdir

with open(f"{ROOT}/game.contract.json", encoding="utf-8") as f:
    C = json.load(f)


def run(cmd, *args):
    return subprocess.run([*shlex.split(cmd), *args], cwd=ROOT, capture_output=True, text=True)


class Phase4(unittest.TestCase):
    def test_manifest_v13(self):
        self.assertEqual(C["contract_version"], "1.3")
        self.assertIn("bench_cmd", C)
        self.assertIn("soak_cmd", C)

    def test_bench_json(self):
        with Workdir() as w:
            p = run(C["bench_cmd"], "--seed", "42", "--duration", "0.5", "--out", w.path("bench.json"))
            self.assertEqual(p.returncode, 0, p.stderr)
            with open(w.path("bench.json"), encoding="utf-8") as f:
                b = json.load(f)
        self.assertEqual(set(b), {"avg_fps", "p1_low_fps", "frames", "measured_s", "load_ms"})
        self.assertGreater(b["frames"], 0)
        self.assertAlmostEqual(b["avg_fps"], b["frames"] / b["measured_s"], delta=1)
        self.assertLessEqual(b["p1_low_fps"], b["avg_fps"] + 1e-6)

    def test_soak_json_va_tat_dinh(self):
        outs = []
        with Workdir() as w:
            for i in (1, 2):
                p = run(C["soak_cmd"], "--seed", "7", "--days", "6", "--out", w.path(f"s{i}.json"))
                self.assertEqual(p.returncode, 0, p.stderr)
                with open(w.path(f"s{i}.json"), encoding="utf-8") as f:
                    outs.append(json.load(f))
        s = outs[0]
        self.assertEqual(set(s), {"days", "days_completed", "crashes", "results", "duration_s"})
        self.assertEqual((s["days"], s["days_completed"], s["crashes"]), (6, 6, 0))
        self.assertEqual([r["day"] for r in s["results"]], list(range(1, 7)))
        self.assertEqual(set(s["results"][0]), {"day", "earned", "reputation", "score"})
        self.assertEqual(outs[0]["results"], outs[1]["results"])  # bỏ duration_s khi so


if __name__ == "__main__":
    unittest.main()
