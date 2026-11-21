"""Phase 3 (contract v1.2): kho cá thể, độ tươi, ươn, giữ chỗ theo id, giá theo tươi, bàn giao kho."""

import json
import unittest

from helpers import Workdir, events, frames, read_jsonl, run_headless, same_items, snapshots

with open("game.contract.json", encoding="utf-8") as f:
    T = json.load(f)["tuning"]


def raw_json(path, obj):  # ghi nguyên dạng, KHÔNG qua migrate (test schema v1.2 thật)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return path


def run(w, mode, ticks, scenario=None, inputs=None, extra=(), out="o.jsonl"):
    args = ["--mode", mode, "--seed", "1", "--ticks", str(ticks), "--out", w.path(out), *extra]
    if scenario is not None:
        args += ["--scenario", raw_json(w.path("sc.json"), scenario)]
    if inputs is not None:
        args += ["--inputs", raw_json(w.path("in.json"), inputs)]
    code, err = run_headless(*args)
    assert code == 0, err
    return read_jsonl(w.path(out))


def item(iid, kind, fresh):
    return {"id": iid, "kind": kind, "fresh": fresh}


class Contract(unittest.TestCase):
    def test_v12_freshness(self):
        with open("game.contract.json", encoding="utf-8") as f:
            c = json.load(f)
        self.assertIn(c["contract_version"], ("1.2", "1.3"))  # v1.3 giữ gameplay v1.2
        self.assertEqual(c["tuning"]["freshness"], {"initial": 100, "gather_decay_per_s": 0.5,
                                                    "quan_decay_per_s": 0.25, "spoiled_below": 30})

    def test_kho_dem_va_sai_schema_ma_2(self):
        with Workdir() as w:
            for bad in ({"items": {"ca_loc": 1}}, {"items": [item("I1", "ca_la_lung", 50)]},
                        {"items": [item("I1", "ca_loc", 50), item("I1", "ca_loc", 60)]},
                        {"items": [item("I1", "ca_loc", 100.5)]}, {"items": [{"id": "I1", "kind": "ca_loc"}]}):
                inv = raw_json(w.path("inv.json"), bad)
                code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--inventory", inv,
                                       "--out", w.path("q.jsonl"))
                self.assertEqual(code, 2, bad)


class Spoil(unittest.TestCase):
    def test_nguong_30_o_buoc_dau(self):
        """Ví dụ của ticket: cá thể bắt đầu đúng fresh 30 ươn ở bước đầu."""
        sc = {"gather": {"hold": [item("I1", "ca_linh", 30)], "random_fish": False, "monsters": []}}
        with Workdir() as w:
            rows = run(w, "gather", 1, sc)
        self.assertEqual([r for r in rows if r["type"] == "event"],
                         [{"type": "event", "tick": 1, "phase": "gather", "name": "spoiled",
                           "data": {"item_id": "I1", "kind": "ca_linh", "location": "hold"}}])

    def test_hao_giu_va_quan(self):
        with Workdir() as w:
            g = run(w, "gather", 60, {"gather": {"hold": [item("I1", "ca_loc", 100)], "random_fish": False,
                                                 "monsters": []}}, extra=("--snapshot-every", "60"))
            q = run(w, "quan", 60, {"quan": {"stock": [item("I1", "ca_loc", 100)], "random_customers": False}},
                    extra=("--snapshot-every", "60"), out="q.jsonl")
        self.assertAlmostEqual(snapshots(g)[-1]["hold"][0]["fresh"], 99.5, delta=0.01)
        self.assertAlmostEqual(snapshots(q)[-1]["stock"][0]["fresh"], 99.75, delta=0.01)

    def test_ban_giao_file_va_quan_doc_lai(self):
        sc = {"gather": {"hold": [item("I1", "ca_linh", 100)], "random_fish": False, "monsters": []}}
        with Workdir() as w:
            inv = w.path("kho.json")
            run(w, "gather", 5, sc, frames({"tick": 0, "interact": True}), extra=("--inventory-out", inv))
            with open(inv, encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved["items"][0]["id"], "I1")
            self.assertAlmostEqual(saved["items"][0]["fresh"], 100 - 0.5 / 60, places=9)
            q = run(w, "quan", 0, extra=("--inventory", inv), out="q.jsonl")
        self.assertTrue(same_items(snapshots(q)[0]["stock"], saved["items"]))

    def test_ngat_ghi_kho_rong(self):
        sc = {"gather": {"hold": [item("I1", "ca_loc", 80)], "random_fish": False, "monsters": [],
                         "player": {"pos": [50, 5], "oxygen_ticks": 0, "hp": 1, "zero_oxy_ticks": 59}}}
        with Workdir() as w:
            inv = w.path("kho.json")
            rows = run(w, "gather", 3, sc, extra=("--inventory-out", inv))
            with open(inv, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"items": []})
        self.assertEqual([x["id"] for x in events(rows, "faint")[0]["data"]["lost"]], ["I1"])


class Quan(unittest.TestCase):
    COOK = {"id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui"}

    def test_giu_tuoi_nhat_va_gia_theo_tuoi(self):
        sc = {"quan": {"stock": [item("I1", "ca_loc", 50), item("I2", "ca_loc", 80)],
                       "customers": [self.COOK], "player": {"pos": [2, 7]}, "random_customers": False}}
        with Workdir() as w:
            rows = run(w, "quan", 2, sc, frames({"tick": 0, "interact": True}), extra=("--snapshot-every", "1"))
        self.assertEqual(snapshots(rows)[0]["customers"][0]["reserved"], ["I2"])  # tươi nhất
        cs = events(rows, "cook_started")[0]["data"]
        self.assertEqual([x["id"] for x in cs["items"]], ["I2"])
        # fresh lúc nấu = 80 - 1/240 -> floor(60 × 79.9958 / 100) = 47
        self.assertEqual(snapshots(rows)[-1]["stoves"][0]["dish"]["base_price"], 47)
        self.assertEqual([x["id"] for x in snapshots(rows)[-1]["stock"]], ["I1"])

    def test_hang_giu_vua_uon_thi_giu_lai(self):
        sc = {"quan": {"stock": [item("I1", "ca_loc", 30), item("I2", "ca_loc", 29)],
                       "customers": [dict(self.COOK, reserved=["I1"])], "random_customers": False}}
        with Workdir() as w:
            rows = run(w, "quan", 1, sc)
        self.assertEqual(events(rows, "spoiled")[0]["data"], {"item_id": "I1", "kind": "ca_loc", "location": "stock"})
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("unfulfillable", []))

    def test_giu_lai_duoc_khi_con_hang_tuoi(self):
        sc = {"quan": {"stock": [item("I1", "ca_loc", 30), item("I2", "ca_loc", 90)],
                       "customers": [dict(self.COOK, reserved=["I1"])], "random_customers": False}}
        with Workdir() as w:
            rows = run(w, "quan", 1, sc)
        c = snapshots(rows)[-1]["customers"][0]
        self.assertEqual((c["order_status"], c["reserved"]), ("reserved", ["I2"]))

    def test_khong_giu_hang_uon(self):
        sc = {"quan": {"stock": [item("I1", "ca_loc", 10)], "customers": [dict(self.COOK, reserved=["I1"])]}}
        with Workdir() as w:
            code, _ = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--out", w.path("o.jsonl"),
                                   "--scenario", raw_json(w.path("sc.json"), sc))
        self.assertEqual(code, 2)


class Day(unittest.TestCase):
    def test_id_tang_xuyen_ngay(self):
        sc = {"gather": {"hold": [item("I1", "ca_loc", 100)], "random_fish": False}}
        inp = frames({"tick": 0, "interact": True}, {"tick": 1, "interact": False}, {"tick": 10802, "shop_done": True},
                     {"tick": 10803, "shop_done": False, "interact": True})
        with Workdir() as w:
            rows = run(w, "day", 10806, sc, inp, extra=("--days", "2", "--snapshot-every", "100000"))
        ends = events(rows, "gather_end")
        self.assertEqual([[x["id"] for x in e["data"]["inventory"]["items"]] for e in ends], [["I1"], ["I2"]])


if __name__ == "__main__":
    unittest.main()
