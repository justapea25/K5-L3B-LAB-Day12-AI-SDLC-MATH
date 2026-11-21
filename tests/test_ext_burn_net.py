"""Mở rộng burn (cháy món) và net (vợt hút cá) — đang bật trong manifest."""

import json
import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim
from chonoi.sim.quan import QuanSim

from helpers import Workdir, events, read_jsonl, run_headless, snapshots

T = load_contract()["tuning"]
BURN = int(T["quan"]["burn_s"] * 60)
NET = T["shop"]["upgrades"]["net"]


def item(iid, kind, fresh=100):
    return {"id": iid, "kind": kind, "fresh": fresh}


def run_quan(w, block, ticks):
    path = w.path("sc.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"quan": block}, f)
    code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", str(ticks), "--scenario", path,
                             "--snapshot-every", "1", "--out", w.path("o.jsonl"))
    assert code == 0, err
    return read_jsonl(w.path("o.jsonl"))


DISH = {"order_id": "C1", "dish_id": "ca_loc_nuong_trui", "base_price": 60}
ASSIGNED = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui", "order_status": "assigned", "reserved": []}


class Burn(unittest.TestCase):
    def test_dung_nguong_van_bung_duoc_qua_nguong_thi_chay(self):
        stove = {"id": "B1", "state": "ready", "dish": DISH, "ready_ticks": BURN - 1}
        with Workdir() as w:
            rows = run_quan(w, {"stock": [], "customers": [ASSIGNED], "stoves": [stove], "random_customers": False}, 3)
        s = {r["tick"]: r for r in snapshots(rows)}
        self.assertEqual(s[1]["stoves"][0]["state"], "ready")  # ready_ticks = BURN: vẫn bưng được
        burnt = events(rows, "dish_burnt")
        self.assertEqual([(e["tick"], e["data"]) for e in burnt],
                         [(2, {"stove_id": "B1", "order_id": "C1", "dish_id": "ca_loc_nuong_trui",
                               "order_status": "unfulfillable"})])
        self.assertEqual(s[2]["stoves"][0]["state"], "idle")

    def test_chay_thi_giu_lai_neu_con_kho(self):
        stove = {"id": "B1", "state": "ready", "dish": DISH, "ready_ticks": BURN}
        with Workdir() as w:
            rows = run_quan(w, {"stock": [item("I5", "ca_loc", 90)], "customers": [ASSIGNED], "stoves": [stove],
                                "random_customers": False}, 1)
        self.assertEqual(events(rows, "dish_burnt")[0]["data"]["order_status"], "reserved")
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I5"]))


class Net(unittest.TestCase):
    def make(self, level, fish, hold=()):
        sc = {"player": {"pos": [50, 10]}, "random_fish": False, "monsters": [], "fish": fish,
              "hold": [item(f"I{90 + i}", k) for i, k in enumerate(hold)]}
        return GatherSim(T, sc, Streams(1), IdAllocator(), net=NET[level - 1] if level else None)

    def catch(self, sim):
        ev = sim.step(InputState((0, 0), {}, {"catch"}))
        return [e for e in ev if e[0] in ("fish_caught", "hold_full")]

    FISH = [{"id": f"F{i}", "kind": "ca_loc", "pos": [50 + i, 10]} for i in (1, 2, 3, 5)]

    def test_cap_0_dung_luat_loi(self):
        ev = self.catch(self.make(0, self.FISH))  # chưa mua vợt: luật lõi, chỉ đàn gần nhất trong 2 m
        self.assertEqual([d["fish_id"] for n, d in ev if n == "fish_caught"], ["F1"])

    def test_cap_1_toi_da_2_dan_trong_4m(self):
        sim = self.make(1, self.FISH)
        ev = self.catch(sim)
        self.assertEqual([d["fish_id"] for n, d in ev if n == "fish_caught"], ["F1", "F2"])
        self.assertGreater(sim.catch_cd_ticks, 0)

    def test_cap_2_toi_da_3_dan_trong_6m(self):
        ev = self.catch(self.make(2, self.FISH))
        self.assertEqual([d["fish_id"] for n, d in ev if n == "fish_caught"], ["F1", "F2", "F3"])

    def test_thieu_cho_bo_qua_dan_do(self):
        fish = [{"id": "F1", "kind": "ca_linh", "pos": [51, 10]}, {"id": "F2", "kind": "ca_loc", "pos": [52, 10]}]
        sim = self.make(1, fish, hold=["bong_sung"] * (T["gather"]["hold_capacity"] - 1))
        ev = self.catch(sim)
        self.assertEqual([n for n, _ in ev], ["hold_full", "fish_caught"])
        self.assertEqual([f["id"] for f in sim.fish], ["F1"])


if __name__ == "__main__":
    unittest.main()
