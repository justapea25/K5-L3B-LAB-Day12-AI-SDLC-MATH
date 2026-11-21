"""Phase 2 (v1.1): cá bơi, Cá Sấu, pause, Shop, chế độ day."""

import json
import unittest

from helpers import Workdir, events, frames, kinds, read_jsonl, run_headless, snapshots, write_json

with open("game.contract.json", encoding="utf-8") as f:
    T = json.load(f)["tuning"]
G = T["gather"]


def run(w, mode, ticks, scenario=None, inputs=None, extra=(), seed=1):
    args = ["--mode", mode, "--seed", str(seed), "--ticks", str(ticks), "--out", w.path("o.jsonl"), *extra]
    if scenario is not None:
        args += ["--scenario", write_json(w.path("sc.json"), scenario)]
    if inputs is not None:
        args += ["--inputs", write_json(w.path("in.json"), inputs)]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path("o.jsonl"))


class FishSwim(unittest.TestCase):
    def test_ca_boi_trong_dai_cua_loai(self):
        with Workdir() as w:
            rows = run(w, "gather", 1200, extra=("--snapshot-every", "100"))
        first, last = snapshots(rows)[0]["fish"], snapshots(rows)[-1]["fish"]
        moved = sum(1 for a, b in zip(first, last) if a["pos"] != b["pos"])
        self.assertGreater(moved, 0)
        for s in snapshots(rows):
            for f in s["fish"]:
                lo, hi = G["fish_depths"][f["kind"]]
                self.assertTrue(G["fish_x"][0] - 1e-3 <= f["pos"][0] <= G["fish_x"][1] + 1e-3, f)
                self.assertTrue(lo - 1e-3 <= f["pos"][1] <= hi + 1e-3, f)

    def test_toc_do_ca(self):
        sc = {"gather": {"fish": [{"id": "F1", "kind": "ca_loc", "pos": [50, 14], "heading_deg": 0}]}}
        with Workdir() as w:
            rows = run(w, "gather", 60, sc, extra=("--snapshot-every", "60"))
        f = snapshots(rows)[-1]["fish"][0]
        self.assertAlmostEqual(f["pos"][0], 50 + G["fish_speed"], places=2)
        self.assertEqual(f["age_ticks"], 60)


class Monster(unittest.TestCase):
    def test_duoi_va_can_mat_nua_gio_lifo(self):
        sc = {"gather": {"player": {"pos": [55, 24]}, "random_fish": False,
                         "hold": ["ca_loc", "ca_linh", "bong_sung", "ca_keo"]}}
        with Workdir() as w:
            rows = run(w, "gather", 80, sc)
        hit = events(rows, "monster_hit")[0]
        # M1 ở [60,24], cách 5 m: đuổi 3 m/s tới khi còn ≤ 1.5 m -> 70 bước
        self.assertEqual(hit["tick"], 71)
        self.assertEqual(dict(hit["data"], lost=kinds(hit["data"]["lost"])), {"monster_id": "M1", "hp": G["hp_max"] - 1,
                                       "lost": ["ca_keo", "bong_sung"], "pos": [55, 24]})
        p = snapshots(rows)[-1]
        self.assertEqual(p["player"]["invuln_ticks"], T["gather"]["monsters"]["invuln_ticks"] - 9)
        self.assertEqual(p["monsters"][0]["state"], "recoil")

    def test_nong_hon_10m_khong_bi_duoi(self):
        sc = {"gather": {"player": {"pos": [58, 5]}, "random_fish": False}}
        with Workdir() as w:
            rows = run(w, "gather", 120, sc)
        self.assertEqual(events(rows, "monster_hit"), [])
        self.assertEqual(snapshots(rows)[-1]["monsters"][0]["state"], "patrol")

    def test_ngat_do_quai(self):
        sc = {"gather": {"player": {"pos": [60, 24], "hp": 1}, "random_fish": False, "hold": ["ca_loc"]}}
        with Workdir() as w:
            rows = run(w, "gather", 5, sc)
        d = events(rows, "faint")[0]["data"]
        self.assertEqual(dict(d, lost=kinds(d["lost"])), {"cause": "monster", "hp": 0, "lost": ["ca_loc"]})
        self.assertEqual(rows[-1]["reason"], "fainted")

    def test_scenario_monsters_rong(self):
        with Workdir() as w:
            rows = run(w, "gather", 1, {"gather": {"monsters": []}})
        self.assertEqual(snapshots(rows)[0]["monsters"], [])


class Pause(unittest.TestCase):
    def test_pause_dung_dong_ho(self):
        inp = frames({"tick": 5, "pause": True}, {"tick": 6, "pause": False}, {"tick": 10, "pause": True})
        with Workdir() as w:
            rows = run(w, "gather", 15, {"gather": {"random_fish": False}}, inp, extra=("--snapshot-every", "1"))
        self.assertEqual([(e["tick"], e["name"]) for e in events(rows) if e["name"] in ("paused", "resumed")],
                         [(6, "paused"), (11, "resumed")])
        s = {r["tick"]: r for r in snapshots(rows)}
        self.assertEqual(s[8]["state"], "paused")
        self.assertEqual(s[8]["sim_tick"], 5)
        self.assertEqual(s[15]["sim_tick"], 10)
        self.assertEqual(s[15]["time_left_ticks"], G["duration_s"] * 60 - 10)


class Day(unittest.TestCase):
    SC = {"day": {"money": 300, "earned": 300}, "gather": {"hold": ["ca_loc"], "random_fish": False}}

    def test_vong_ngay_va_shop(self):
        inp = frames({"tick": 0, "interact": True}, {"tick": 10802, "buy": "oxygen"},
                     {"tick": 10803, "shop_done": True})
        with Workdir() as w:
            rows = run(w, "day", 40000, self.SC, inp, extra=("--days", "2", "--snapshot-every", "1000"))
        names = [(e["tick"], e["phase"], e["name"]) for e in events(rows)
                 if e["name"] in ("day_start", "day_plan", "phase_start", "gather_end", "quan_end",
                                  "bought", "shop_end")]
        self.assertEqual(names[:9], [(0, "gather", "day_start"), (0, "gather", "day_plan"),
                                     (0, "gather", "phase_start"), (1, "gather", "gather_end"),
                                     (1, "quan", "phase_start"), (10801, "quan", "quan_end"),
                                     (10801, "shop", "phase_start"), (10803, "shop", "bought"),
                                     (10804, "shop", "shop_end")])
        bought = events(rows, "bought")[0]["data"]
        self.assertEqual(bought, {"upgrade": "oxygen", "level": 1, "price": 200, "money": 100})
        day2 = [s for s in snapshots(rows) if s["day"] == 2 and s["phase"] == "gather"][0]
        self.assertEqual(day2["active_upgrades"], {"oxygen": 1})
        self.assertEqual(day2["player"]["oxygen_max_ticks"], 45 * 60)
        end = rows[-1]
        self.assertEqual((end["reason"], end["days_completed"]), ("days_complete", 2))

    def test_buy_failed(self):
        inp = frames({"tick": 0, "interact": True}, {"tick": 10802, "buy": "hp"}, {"tick": 10803, "buy": "weapon"})
        with Workdir() as w:
            rows = run(w, "day", 10805, {"gather": {"random_fish": False}}, inp)
        self.assertEqual([e["data"] for e in events(rows, "buy_failed")],
                         [{"action": "hp", "reason": "funds"}, {"action": "weapon", "reason": "unknown"}])  # weapon chưa bật

    def test_mot_ngay_khong_pause_22200_tick(self):
        with Workdir() as w:
            rows = run(w, "day", 30000, {"gather": {"random_fish": False}}, extra=("--snapshot-every", "1000"))
        self.assertEqual(rows[-1]["ticks"], 22200)
        self.assertEqual(rows[-1]["reason"], "days_complete")

    def test_day_cam_quan_stock_va_days_sai(self):
        with Workdir() as w:
            for sc, extra in (({"quan": {"stock": {}}}, ()), ({}, ("--days", "6"))):
                args = ["--mode", "day", "--seed", "1", "--ticks", "0", "--out", w.path("x.jsonl"),
                        "--scenario", write_json(w.path("sc.json"), sc), *extra]
                self.assertEqual(run_headless(*args)[0], 2, (sc, extra))
            args = ["--mode", "gather", "--days", "2", "--seed", "1", "--ticks", "0", "--out", w.path("x.jsonl")]
            self.assertEqual(run_headless(*args)[0], 2)


if __name__ == "__main__":
    unittest.main()
