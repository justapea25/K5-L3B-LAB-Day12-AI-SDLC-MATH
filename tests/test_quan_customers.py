"""Test lát 3 (@viethoang127): khách của quán — đến theo lịch, chọn món, giữ chỗ, kiên nhẫn, bỏ đi, no_dish,
và khách dựng sẵn từ scenario. Dữ liệu thử tự dựng trong file này; không sửa game.contract.json.

Hàm lát 3 được gọi trực tiếp trên một QuanSim thật (quan.py chưa cần gọi chúng).
"""

import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim
from chonoi.sim.quan_customers import (build_fixture_customers, customers_leave, remove_customer,
                                       spawn_customers, tick_customers, tick_customers_timers)

from chonoi.inventory import validate_item_list
from helpers import Workdir, read_jsonl, run_headless, snapshots, to_items, write_json

TUNING = load_contract()["tuning"]
Q = TUNING["quan"]
PATIENCE = int(round(Q["patience_s"] * 60))
EAT = int(round(Q["eat_s"] * 60))
FIRST = Q["first_customer_tick"]
INTERVAL = int(round(Q["customer_interval_s"] * 60))
ALL_STOCK = {"ca_loc": 1, "bong_sung": 2, "ca_linh": 3, "bong_dien_dien": 1}


def _stock(stock):
    """v1.2: dict đếm / mảng cá thể ngoài -> cá thể nội bộ; cá thể nội bộ (có units) giữ nguyên."""
    if stock is None or (isinstance(stock, list) and stock and "units" in stock[0]):
        return stock
    return validate_item_list(to_items(stock))


def _raw(customers):
    """v1.2: reserved theo lượng -> bỏ để hệ thống tự cấp theo id; {} -> []."""
    out = []
    for c in customers:
        c = dict(c)
        if isinstance(c.get("reserved"), dict):
            if c["reserved"]:
                del c["reserved"]
            else:
                c["reserved"] = []
        out.append(c)
    return out


def bfc(raw, tuning, stock=None, *a):
    return build_fixture_customers(_raw(raw), tuning, _stock(stock), *a)


def reserved_counts(sim_or_stock, c):
    stock = sim_or_stock.stock if hasattr(sim_or_stock, "stock") else sim_or_stock
    by = {it["id"]: it["kind"] for it in stock}
    out = {}
    for iid in c["reserved"]:
        out[by[iid]] = out.get(by[iid], 0) + 1
    return out


def make_sim(stock=None, customers=None, seed=1, **scenario):
    sc = dict(scenario)
    sc["stock"] = to_items(ALL_STOCK if stock is None else stock)
    if customers is not None:
        sc["customers"] = bfc(customers, TUNING, sc["stock"])
    sim = QuanSim(TUNING, sc, Streams(seed), IdAllocator())
    sim.phase_tick = FIRST
    return sim


def waiting(cid="C1", table="T1", dish="goi_bong_sung", **kw):
    return dict({"id": cid, "table_id": table, "dish_id": dish}, **kw)


class Spawn(unittest.TestCase):
    def test_first_customer_at_first_tick_only(self):
        sim = make_sim()
        sim.phase_tick = FIRST - 1
        ev = []
        spawn_customers(sim, ev)
        self.assertEqual((ev, sim.customers), ([], []))
        sim.phase_tick = FIRST
        spawn_customers(sim, ev)
        self.assertEqual([e[0] for e in ev], ["customer_arrived"])
        c = sim.customers[0]
        self.assertEqual((c["id"], c["table_id"], c["state"], c["order_status"]), ("C1", "T1", "waiting", "reserved"))
        self.assertEqual(c["order_tick"], FIRST)
        self.assertEqual(c["patience_ticks_left"], PATIENCE)
        self.assertEqual(ev[0][1], {"order_id": "C1", "table_id": "T1", "dish_id": c["dish_id"]})

    def test_reserves_exact_recipe(self):
        sim = make_sim()
        spawn_customers(sim, [])
        c = sim.customers[0]
        self.assertEqual(reserved_counts(sim, c), TUNING["menu"][c["dish_id"]]["recipe"])  # v1.2: mảng id

    def test_next_customers_every_interval(self):
        sim = make_sim()
        spawn_customers(sim, [])
        remove_customer(sim, sim.customers[0])
        ev = []
        sim.phase_tick = FIRST + INTERVAL - 1
        spawn_customers(sim, ev)
        self.assertEqual(ev, [])
        sim.phase_tick = FIRST + INTERVAL
        spawn_customers(sim, ev)
        self.assertEqual(ev[0][1]["order_id"], "C2", "id nối tiếp, không cấp lại")

    def test_no_dish_when_stock_cannot_cook_anything(self):
        sim = make_sim(stock={"ca_linh": 2})
        ev = []
        spawn_customers(sim, ev)
        self.assertEqual(ev, [("no_dish", {})])
        self.assertEqual(sim.customers, [])

    def test_reserved_stock_is_not_available_again(self):
        # ca_loc duy nhất đã giữ cho C1 -> không còn món nào nấu được cho khách mới
        sim = make_sim(stock={"ca_loc": 1},
                       customers=[waiting("C1", "T1", "ca_loc_nuong_trui")])
        sim.tables.append({"id": "T2", "pos": [10, 2]})
        ev = []
        spawn_customers(sim, ev)
        self.assertEqual(ev, [("no_dish", {})])

    def test_no_free_table_skips_turn_silently(self):
        # v1.1 có 4 bàn: phải kín hết bàn mới bỏ lượt (P1 chỉ có T1)
        full = [waiting(f"C{i}", tb["id"]) for i, tb in enumerate(TUNING["quan"]["tables"], 1)]
        sim = make_sim(stock=dict(ALL_STOCK, bong_sung=2 * len(full)), customers=full)
        ev = []
        spawn_customers(sim, ev)
        self.assertEqual(ev, [])
        self.assertEqual(len(sim.customers), len(full))

    def test_lowest_free_table_id_first(self):
        sim = make_sim(customers=[waiting("C1", "T1")])
        sim.tables.extend([{"id": "T10", "pos": [1, 1]}, {"id": "T2", "pos": [2, 2]}])
        spawn_customers(sim, [])
        new = [c for c in sim.customers if c["id"] == "C2"][0]
        self.assertEqual(new["table_id"], "T2", "T2 đứng trước T10")

    def test_no_spawn_when_closed_or_random_off(self):
        sim = make_sim()
        sim.time_left_ticks = 0
        spawn_customers(sim, [])
        self.assertEqual(sim.customers, [])
        sim = make_sim()
        sim.random_customers = False
        spawn_customers(sim, [])
        self.assertEqual(sim.customers, [])

    def test_choice_is_seeded_and_only_feasible(self):
        picks = []
        for seed in range(30):
            sim = make_sim(seed=seed)
            spawn_customers(sim, [])
            picks.append(sim.customers[0]["dish_id"])
            again = make_sim(seed=seed)
            spawn_customers(again, [])
            self.assertEqual(again.customers[0]["dish_id"], picks[-1], "cùng seed phải cùng món")
        self.assertGreater(len(set(picks)), 1, "chọn ngẫu nhiên giữa các món đủ nguyên liệu")
        sim = make_sim(stock={"bong_sung": 2})
        spawn_customers(sim, [])
        self.assertEqual(sim.customers[0]["dish_id"], "goi_bong_sung")


class TickAndLeave(unittest.TestCase):
    def test_timers_only_waiting_patience_never_eat_timer(self):
        sim = make_sim(stock={"bong_sung": 4})
        sim.tables.append({"id": "T2", "pos": [10, 2]})
        sim.customers = bfc([
            waiting("C1", "T1", patience_ticks_left=10, reserved={"bong_sung": 2}),
            waiting("C2", "T2", state="eating", order_status="served", eat_ticks_left=5,
                    patience_ticks_left=7, base_price=40, tip=0)], TUNING, sim.stock)
        tick_customers_timers(sim, [])
        c1, c2 = sim.customers
        self.assertEqual((c1["patience_ticks_left"], c1["eat_ticks_left"]), (9, 0))
        self.assertEqual((c2["patience_ticks_left"], c2["eat_ticks_left"]), (7, 5),
                         "khách ăn: kiên nhẫn đứng yên, timer ăn do lát 4 giảm (không giảm đôi)")

    def test_patience_zero_leaves_and_costs_reputation(self):
        sim = make_sim(customers=[waiting("C1", "T1", patience_ticks_left=0)])
        ev = []
        customers_leave(sim, ev)
        self.assertEqual(sim.customers, [])
        rep = Q["reputation_initial"] + Q["left_reputation_delta"]
        self.assertEqual(sim.reputation, rep)
        self.assertEqual(ev, [("customer_left", {"order_id": "C1", "table_id": "T1",
                                                 "reason": "patience", "reputation": rep})])

    def test_still_patient_stays(self):
        sim = make_sim(customers=[waiting("C1", "T1", patience_ticks_left=1)])
        ev = []
        customers_leave(sim, ev)
        self.assertEqual((len(sim.customers), ev), (1, []))

    def test_reputation_clamped_at_min(self):
        sim = make_sim(customers=[waiting("C1", "T1", patience_ticks_left=0)])
        sim.reputation = Q["reputation_min"]
        customers_leave(sim, [])
        self.assertEqual(sim.reputation, Q["reputation_min"])

    def test_leave_cleans_stove_and_hand(self):
        sim = make_sim(customers=[waiting("C1", "T1", patience_ticks_left=0)])
        sim.stoves[0].update(state="cooking", cook_ticks_left=50, dish={"order_id": "C1", "dish_id": "goi_bong_sung"})
        sim.hand = {"order_id": "C1", "dish_id": "goi_bong_sung", "base_price": 40}
        customers_leave(sim, [])
        self.assertEqual((sim.stoves[0]["state"], sim.stoves[0]["dish"], sim.hand), ("idle", None, None))

    def test_closing_waiting_leave_without_reputation_cost_eating_stays(self):
        sim = make_sim(stock={"bong_sung": 4})
        sim.tables.append({"id": "T2", "pos": [10, 2]})
        sim.customers = bfc([
            waiting("C1", "T1", reserved={"bong_sung": 2}),
            waiting("C2", "T2", state="eating", order_status="served", eat_ticks_left=5,
                    base_price=40, tip=0)], TUNING, sim.stock)
        sim.time_left_ticks = 0
        ev = []
        customers_leave(sim, ev)
        self.assertEqual([c["id"] for c in sim.customers], ["C2"])
        self.assertEqual(ev[0][1]["reason"], "closing")
        self.assertEqual(sim.reputation, Q["reputation_initial"])

    def test_leave_events_ordered_by_table_id(self):
        sim = make_sim(stock={"bong_sung": 6})
        sim.tables.extend([{"id": "T2", "pos": [10, 2]}, {"id": "T10", "pos": [11, 2]}])
        sim.customers = bfc([
            waiting("C1", "T10", patience_ticks_left=0, reserved={"bong_sung": 2}),
            waiting("C2", "T2", patience_ticks_left=0, reserved={"bong_sung": 2}),
            waiting("C3", "T1", patience_ticks_left=0, reserved={"bong_sung": 2})], TUNING, sim.stock)
        ev = []
        customers_leave(sim, ev)
        self.assertEqual([e[1]["table_id"] for e in ev], ["T1", "T2", "T10"])

    def test_old_name_tick_customers_wraps_new_functions(self):
        sim = make_sim(customers=[waiting("C1", "T1", patience_ticks_left=1)])
        ev = []
        tick_customers(sim, ev)  # all: timers rồi leave -> kiên nhẫn 0 -> rời
        self.assertEqual([e[1]["reason"] for e in ev], ["patience"])
        with self.assertRaises(ValueError):
            tick_customers(make_sim(), [], "x")


class Fixture(unittest.TestCase):
    def build(self, raw, stock=None, stoves=(), hand=None):
        return bfc(raw, TUNING, stock, stoves, hand)

    def test_defaults_and_derived_reserved(self):
        stock = _stock({"ca_linh": 3, "bong_dien_dien": 1})
        c = self.build([waiting("C1", "T1", "lau_ca_linh_dien_dien")], stock=stock)[0]
        self.assertEqual((c["state"], c["order_status"], c["order_tick"]), ("waiting", "reserved", 0))
        self.assertEqual((c["patience_ticks_left"], c["eat_ticks_left"]), (PATIENCE, 0))
        self.assertEqual(reserved_counts(stock, c), {"ca_linh": 3, "bong_dien_dien": 1})  # v1.2: mảng id

    def test_sorted_by_id(self):
        out = self.build([waiting("C10", "T10"), waiting("C2", "T2")])
        self.assertEqual([c["id"] for c in out], ["C2", "C10"])

    def test_reserved_over_stock_rejected(self):
        with self.assertRaises(BadInput):
            self.build([waiting("C1", "T1", "ca_loc_nuong_trui")], stock={})
        with self.assertRaises(BadInput):
            self.build([waiting("C1", "T1"), waiting("C2", "T2")], stock={"bong_sung": 3})

    def test_reserved_must_match_recipe(self):
        with self.assertRaises(BadInput):
            self.build([waiting(reserved=["I1"])], stock={"bong_sung": 2})  # v1.2: giữ 1 id thiếu công thức

    def test_bad_fields(self):
        for bad in (waiting(dish_id_x=1), waiting(state="sleeping"), waiting(order_status="x"),
                    waiting(patience_ticks_left=-1), waiting(patience_ticks_left=PATIENCE + 1),
                    waiting(eat_ticks_left=3), waiting(dish="zzz")):
            with self.assertRaises(BadInput, msg=bad):
                self.build([bad])
        with self.assertRaises(BadInput):
            self.build([{"id": "C1", "table_id": "T1", "dish_id": "khong_co"}])
        with self.assertRaises(BadInput):
            self.build([{"id": "C1", "table_id": "T1"}])

    def test_eating_rules(self):
        ok = waiting(state="eating", order_status="served", eat_ticks_left=EAT, base_price=40, tip=8)
        self.assertEqual(self.build([ok])[0]["reserved"], [])
        for bad in (dict(ok, eat_ticks_left=0), {k: v for k, v in ok.items() if k != "tip"},
                    {k: v for k, v in ok.items() if k != "base_price"},
                    dict(ok, order_status="reserved"), waiting(order_status="served")):
            with self.assertRaises(BadInput, msg=bad):
                self.build([bad])

    def test_assigned_needs_exactly_one_dish(self):
        c = waiting(order_status="assigned", reserved={})
        payload = {"order_id": "C1", "dish_id": "goi_bong_sung", "base_price": 40}
        stove = {"id": "B1", "state": "cooking", "cook_ticks_left": 20, "dish": payload}
        self.assertEqual(self.build([c], stoves=[stove])[0]["order_status"], "assigned")
        self.assertEqual(self.build([c], hand=payload)[0]["order_status"], "assigned")
        with self.assertRaises(BadInput):   # không có món
            self.build([c])
        with self.assertRaises(BadInput):   # bếp và tay cùng giữ
            self.build([c], stoves=[stove], hand=payload)
        with self.assertRaises(BadInput):   # món không khớp dish_id
            self.build([c], hand=dict(payload, dish_id="ca_loc_nuong_trui"))
        with self.assertRaises(BadInput):   # assigned mà còn giữ chỗ
            self.build([waiting(order_status="assigned", reserved=["I1", "I2"])], hand=payload)
        with self.assertRaises(BadInput):   # bếp cooking timer 0
            self.build([c], stoves=[dict(stove, cook_ticks_left=0)])

    def test_unfulfillable_and_reserved_have_no_dish(self):
        payload = {"order_id": "C1", "dish_id": "goi_bong_sung", "base_price": 40}
        self.assertEqual(self.build([waiting(order_status="unfulfillable")])[0]["reserved"], [])
        with self.assertRaises(BadInput):
            self.build([waiting(order_status="unfulfillable")], hand=payload)
        with self.assertRaises(BadInput):
            self.build([waiting()], hand=payload)

    def test_stove_dish_of_unknown_order_rejected(self):
        stove = {"id": "B1", "state": "ready", "dish": {"order_id": "C9", "dish_id": "goi_bong_sung"}}
        with self.assertRaises(BadInput):
            self.build([], stoves=[stove])


class BlackBox(unittest.TestCase):
    """Qua headless: scenario sai -> mã 2; scenario đúng -> khách có trong snapshot tick 0."""

    def run_scenario(self, block, w):
        sc = write_json(w.path("sc.json"), {"quan": block})
        code, err = run_headless("--mode", "quan", "--seed", "1", "--ticks", "0", "--scenario", sc,
                                 "--out", w.path("o.jsonl"))
        return code, err

    def test_valid_fixture_visible_in_snapshot(self):
        with Workdir() as w:
            block = {"stock": {"bong_sung": 2},
                     "customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung"}]}
            code, err = self.run_scenario(block, w)
            self.assertEqual(code, 0, err)
            c = snapshots(read_jsonl(w.path("o.jsonl")))[0]["customers"][0]
            self.assertEqual((c["id"], c["table_id"], c["dish_id"]), ("C1", "T1", "goi_bong_sung"))

    def test_bad_customers_exit_2(self):
        bad = [
            {"customers": [{"id": "C1", "table_id": "T1", "dish_id": "khong_co"}]},
            {"stock": {}, "customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung"}]},
            {"customers": [{"id": "C1", "table_id": "T1", "dish_id": "goi_bong_sung", "state": "eating"}]},
            {"random_customers": "no"},
        ]
        for block in bad:
            with Workdir() as w:
                self.assertEqual(self.run_scenario(block, w)[0], 2, block)


if __name__ == "__main__":
    unittest.main()
