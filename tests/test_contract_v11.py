"""Contract v1.1: số chuẩn, kế hoạch ngày, sinh cá đầu ca / theo lịch, faint theo v1.1."""

import json
import math
import unittest

from helpers import Workdir, events, kinds, read_jsonl, run_headless, snapshots, write_json


def contract():
    with open("game.contract.json", encoding="utf-8") as f:
        return json.load(f)


T = contract()["tuning"]
G = T["gather"]


def run(w, ticks, scenario=None, seed=1):
    args = ["--mode", "gather", "--seed", str(seed), "--ticks", str(ticks), "--out", w.path(f"o{seed}.jsonl")]
    if scenario is not None:
        args += ["--scenario", write_json(w.path("sc.json"), {"gather": scenario})]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path(f"o{seed}.jsonl"))


class Contract(unittest.TestCase):
    def test_version_va_du_lieu_chuan(self):
        c = contract()
        self.assertIn(c["contract_version"], ("1.2", "1.3"))  # v1.3 giữ gameplay v1.2  # contract đã lên v1.2 (Phase 3)
        self.assertEqual(len(T["menu"]), 6)
        self.assertEqual([n["id"] for n in G["nodes"]], ["N1", "N2", "N3", "N4", "N5", "N6"])
        self.assertEqual(G["fish_yield"], {"ca_linh": 3, "ca_loc": 1, "ca_keo": 2})
        self.assertEqual([s["id"] for s in T["quan"]["stoves"]], ["B1", "B2"])
        self.assertEqual([t["id"] for t in T["quan"]["tables"]], ["T1", "T2", "T3", "T4"])

    def test_day_plan_khop_de(self):
        slots = [sum(d["ingredients"].values()) for d in T["day_plan"]]
        self.assertEqual(slots, [9, 10, 12, 9, 10])
        self.assertEqual(T["day_plan"][0]["ingredients"], {"bong_sung": 6, "ca_loc": 3})


class FishSpawn(unittest.TestCase):
    def test_dau_ca_8_dan_o_diem_khac_nhau(self):
        with Workdir() as w:
            fish = snapshots(run(w, 0))[0]["fish"]
        self.assertEqual(len(fish), G["fish_initial"])
        for f in fish:
            self.assertIn(f["pos"][0], G["fish_spawn_x"])
            self.assertIn(f["pos"][1], G["fish_spawn_depths"][f["kind"]])
        for i, a in enumerate(fish):
            for b in fish[i + 1:]:
                self.assertGreater(math.dist(a["pos"], b["pos"]), G["fish_spawn_clearance"])

    def test_cung_seed_cung_dan_khac_seed_khac_dan(self):
        with Workdir() as w:
            a = snapshots(run(w, 0, seed=1))[0]["fish"]
            b = snapshots(run(w, 0, seed=1))[0]["fish"]
            c = snapshots(run(w, 0, seed=2))[0]["fish"]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_sinh_theo_lich(self):
        with Workdir() as w:
            rows = run(w, 2 * G["fish_spawn_ticks"] + 1, {"player": {"pos": [2, 0]}})
        ev = events(rows, "fish_spawned")
        self.assertEqual([e["tick"] for e in ev], [G["fish_spawn_ticks"], 2 * G["fish_spawn_ticks"]])
        self.assertEqual(ev[0]["data"]["id"], f"F{G['fish_initial'] + 1}")

    def test_random_fish_false_khong_sinh(self):
        with Workdir() as w:
            rows = run(w, G["fish_spawn_ticks"] + 1, {"random_fish": False})
        self.assertEqual(snapshots(rows)[0]["fish"], [])
        self.assertEqual(events(rows, "fish_spawned"), [])


class Faint(unittest.TestCase):
    def test_faint_v11_hp_0_lost_theo_lifo(self):
        with Workdir() as w:
            rows = run(w, 5, {"hold": ["ca_loc", "bong_sung", "ca_keo"],
                              "player": {"pos": [50, 5], "oxygen_ticks": 0, "hp": 1,
                                         "zero_oxy_ticks": G["choke_interval_ticks"] - 1}})
        data = events(rows, "faint")[0]["data"]
        self.assertEqual(dict(data, lost=kinds(data["lost"])),
                         {"cause": "choke", "hp": 0, "lost": ["ca_keo", "bong_sung", "ca_loc"]})  # v1.2: kho cá thể


if __name__ == "__main__":
    unittest.main()
