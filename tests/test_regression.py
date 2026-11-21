"""Hồi quy khi đổi pha và tạm dừng với kho cá thể."""

import unittest

from chonoi.contract import load_contract
from helpers import Workdir, events, frames, read_jsonl, run_headless, snapshots, write_json


class DayHandoffRegression(unittest.TestCase):
    def test_ban_giao_hang_uon_va_pause_khong_hao_tuoi(self):
        """AC-P2-13, AC-P2-18, AC-P3-05, AC-P3-08."""
        tuning = load_contract()["tuning"]
        freshness = tuning["freshness"]
        initial = freshness["initial"]
        threshold = freshness["spoiled_below"]
        scenario = {
            "gather": {
                "hold": [
                    {"id": "I1", "kind": "ca_loc", "fresh": threshold},
                    {"id": "I2", "kind": "bong_sung", "fresh": initial},
                ],
                "random_fish": False,
                "monsters": [],
            },
            "quan": {"random_customers": False},
        }
        inputs = frames(
            {"tick": 0, "interact": True},
            {"tick": 1, "pause": True},
            {"tick": 2, "pause": False},
            {"tick": 3, "pause": True},
        )
        with Workdir() as work:
            output = work.path("day.jsonl")
            code, stderr = run_headless(
                "--mode", "day", "--days", "1", "--seed", "1", "--ticks", "4",
                "--scenario", write_json(work.path("scenario.json"), scenario),
                "--inputs", write_json(work.path("inputs.json"), inputs),
                "--out", output, "--snapshot-every", "1",
            )
            self.assertEqual(code, 0, stderr)
            rows = read_jsonl(output)

        handoff = [event for event in events(rows) if event["tick"] == 1]
        self.assertEqual([event["name"] for event in handoff],
                         ["spoiled", "gather_end", "phase_start"])
        self.assertEqual(handoff[0]["data"]["item_id"], "I1")
        self.assertEqual(handoff[-1]["phase"], "quan")
        saved = handoff[1]["data"]["inventory"]["items"]
        self.assertEqual([(item["id"], item["kind"]) for item in saved],
                         [("I1", "ca_loc"), ("I2", "bong_sung")])
        self.assertLess(saved[0]["fresh"], threshold)
        gather_decay = freshness["gather_decay_per_s"] / 60
        self.assertEqual([item["fresh"] for item in saved],
                         [round(fresh - gather_decay, 3) for fresh in (threshold, initial)])

        by_tick = {snapshot["tick"]: snapshot for snapshot in snapshots(rows)}
        for tick in (1, 2, 3):
            with self.subTest(tick=tick):
                self.assertEqual(by_tick[tick]["phase"], "quan")
                self.assertEqual(by_tick[tick]["phase_tick"], 0)
                self.assertEqual(by_tick[tick]["stock"], saved)
        self.assertEqual(by_tick[2]["state"], "paused")
        self.assertEqual(by_tick[3]["state"], "paused")
        self.assertEqual(by_tick[4]["state"], "playing")
        self.assertEqual(by_tick[4]["phase_tick"], 1)
        quan_decay = freshness["quan_decay_per_s"] / 60
        self.assertEqual([(item["id"], item["kind"]) for item in by_tick[4]["stock"]],
                         [("I1", "ca_loc"), ("I2", "bong_sung")])
        for item, fresh in zip(by_tick[4]["stock"], (threshold, initial)):
            self.assertAlmostEqual(item["fresh"], fresh - gather_decay - quan_decay, delta=0.001)
        self.assertEqual(len(events(rows, "spoiled")), 1)
