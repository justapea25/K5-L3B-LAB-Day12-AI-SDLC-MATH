"""Kỹ năng thêm của Gather: giữ F phóng to lưới, giữ G tăng tốc (gather_skills.py).

Tắt mặc định (contract: skills.enabled=false). Test lõi: khi tắt thì luật gốc không đổi.
Phần bật dựng GatherSim trực tiếp với bản sao tuning có skills.enabled=true.
"""

import copy
import unittest

from helpers import Workdir, frames, run_headless, write_json

from chonoi.contract import load_contract, validate_tuning
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim

BASE = load_contract()["tuning"]
G = BASE["gather"]
SK = BASE["skills"]
OXY_MAX = int(round(G["oxygen_max_s"] * 60))


def make_sim(scenario, enabled=True):
    t = copy.deepcopy(BASE)
    t["skills"]["enabled"] = enabled
    return GatherSim(t, scenario, Streams(1), IdAllocator())


def inp(move=(0.0, 0.0), held=(), edges=()):
    return InputState(move, {b: (b in held) for b in ("net", "sprint", "catch", "interact")}, set(edges))


def fish(fid, pos, kind="ca_loc"):
    return {"id": fid, "kind": kind, "pos": pos, "heading_deg": 0}


def names(events):
    return [n for n, _ in events]


class Disabled(unittest.TestCase):
    def test_contract_mac_dinh_tat(self):
        self.assertIs(SK["enabled"], False)

    def test_headless_phim_f_g_khong_doi_luat_goc(self):
        with Workdir() as w:
            plain = write_json(w.path("a.json"), frames({"tick": 0, "move": [1, 1]}, {"tick": 100, "move": [0, 0]}))
            skill = write_json(w.path("b.json"), frames({"tick": 0, "move": [1, 1], "net": True, "sprint": True},
                                                        {"tick": 100, "move": [0, 0]}))
            for name, path in (("a", plain), ("b", skill)):
                code, err = run_headless("--mode", "gather", "--seed", "3", "--ticks", "300", "--inputs", path,
                                         "--out", w.path(f"{name}.jsonl"))
                self.assertEqual(code, 0, err)
            with open(w.path("a.jsonl"), "rb") as fa, open(w.path("b.jsonl"), "rb") as fb:
                self.assertEqual(fa.read(), fb.read())

    def test_tat_thi_giu_phim_khong_co_tac_dung(self):
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": [fish("F1", [53, 10])]}, enabled=False)
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual(names(ev), [])
        self.assertEqual(len(sim.fish), 1)
        self.assertEqual(sim.oxygen_ticks, OXY_MAX - 1)
        self.assertNotIn("skills", sim.snapshot()["player"])

    def test_snapshot_chi_co_skills_khi_bat(self):
        self.assertIn("skills", make_sim({}).snapshot()["player"])


class Net(unittest.TestCase):
    def test_luoi_bat_duoc_ca_ngoai_ban_kinh_goc(self):
        far = 50 + (G["catch_radius"] + SK["net_radius"]) / 2  # nằm giữa hai bán kính
        sc = {"player": {"pos": [50, 10]}, "nodes": [], "fish": [fish("F1", [far, 10])]}
        sim = make_sim(sc)
        self.assertEqual(names(sim.step(inp(edges=("catch",)))), [])
        sim = make_sim(sc)
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual(names(ev), ["fish_caught"])
        self.assertEqual(sim.fish, [])

    def test_luoi_bat_nhieu_dan_gan_nhat_truoc_va_hoi_chieu_mot_lan(self):
        fs = [fish("F1", [53, 10]), fish("F2", [51, 10]), fish("F3", [52, 10])]
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": fs})
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual([d["fish_id"] for n, d in ev if n == "fish_caught"], ["F2", "F3", "F1"])
        self.assertEqual(sim.catch_cd_ticks, int(round(G["catch_cooldown_s"] * 60)))

    def test_khong_giu_luoi_chi_bat_mot_dan(self):
        fs = [fish("F1", [51, 10]), fish("F2", [51.5, 10])]
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": fs})
        ev = sim.step(inp(edges=("catch",)))
        self.assertEqual(names(ev), ["fish_caught"])
        self.assertEqual(len(sim.fish), 1)

    def test_toi_da_net_max_schools(self):
        n = SK["net_max_schools"] + 2
        fs = [fish(f"F{i + 1}", [50 + 0.1 * (i + 1), 10]) for i in range(n)]
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": fs})
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual(names(ev).count("fish_caught"), SK["net_max_schools"])
        self.assertEqual(len(sim.fish), 2)

    def test_gio_day_giua_chung_dung_lai_nhung_van_hoi_chieu(self):
        # F1 (ca_loc, 1 món) vừa; sau đó giỏ không đủ chỗ cho F2 (ca_linh, nhiều món).
        need = G["fish_yield"]["ca_linh"]
        used = G["hold_capacity"] - 1 - (need - 1)
        hold = [{"id": f"I{i + 1}", "kind": "ca_loc", "fresh": 100} for i in range(used)]
        fs = [fish("F1", [51, 10], "ca_loc"), fish("F2", [52, 10], "ca_linh")]
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": fs, "hold": hold})
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual(names(ev), ["fish_caught", "hold_full"])
        self.assertEqual([f["id"] for f in sim.fish], ["F2"])
        self.assertGreater(sim.catch_cd_ticks, 0)

    def test_gio_day_ngay_tu_dau_khong_hoi_chieu(self):
        hold = [{"id": f"I{i + 1}", "kind": "ca_loc", "fresh": 100} for i in range(G["hold_capacity"])]
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": [fish("F1", [51, 10])], "hold": hold})
        ev = sim.step(inp(held=("net",), edges=("catch",)))
        self.assertEqual(names(ev), ["hold_full"])
        self.assertEqual(sim.catch_cd_ticks, 0)

    def test_giu_luoi_tru_them_oxy_duoi_nuoc(self):
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": []})
        sim.step(inp(held=("net",)))
        self.assertEqual(sim.oxygen_ticks, OXY_MAX - 1 - SK["net_extra_oxygen_ticks"])
        self.assertTrue(sim.snapshot()["player"]["skills"]["net_on"])


class Sprint(unittest.TestCase):
    @staticmethod
    def run_swim(held, ticks=90):
        sim = make_sim({"player": {"pos": [10, 0]}, "nodes": [], "fish": []})
        for _ in range(ticks):
            sim.step(inp(move=(1.0, 0.0), held=held))
        return sim

    def test_giu_g_di_nhanh_hon(self):
        base = self.run_swim(()).pos[0] - 10
        fast = self.run_swim(("sprint",)).pos[0] - 10
        self.assertGreater(fast, base * (SK["sprint_speed_mult"] - 0.1))

    def test_nha_g_ve_toc_do_thuong(self):
        sim = self.run_swim(("sprint",), 60)
        for _ in range(G["ramp_max_ticks"] + 2):
            sim.step(inp(move=(1.0, 0.0)))
        self.assertAlmostEqual(sim.vel[0], G["swim_speed"], places=3)

    def test_giu_g_tru_them_oxy_duoi_nuoc(self):
        sim = make_sim({"player": {"pos": [50, 10]}, "nodes": [], "fish": []})
        for _ in range(60):
            sim.step(inp(held=("sprint",)))
        self.assertEqual(sim.oxygen_ticks, OXY_MAX - 60 * (1 + SK["sprint_extra_oxygen_ticks"]))

    def test_o_mat_nuoc_khong_ton_them_oxy(self):
        sim = make_sim({"player": {"pos": [50, 0], "oxygen_ticks": 100}, "nodes": [], "fish": []})
        sim.step(inp(held=("sprint",)))
        self.assertGreaterEqual(sim.oxygen_ticks, 100)


class ContractCheck(unittest.TestCase):
    def test_skills_sai_bi_tu_choi(self):
        for key, bad in (("net_radius", 99), ("net_max_schools", 0), ("sprint_speed_mult", 0.5),
                         ("net_extra_oxygen_ticks", -1), ("enabled", "yes")):
            t = copy.deepcopy(BASE)
            t["skills"][key] = bad
            with self.assertRaises(BadInput, msg=key):
                validate_tuning(t, t.get("extensions", []))

    def test_khong_khai_skills_van_hop_le(self):
        t = copy.deepcopy(BASE)
        del t["skills"]
        validate_tuning(t, t.get("extensions", []))


if __name__ == "__main__":
    unittest.main()
