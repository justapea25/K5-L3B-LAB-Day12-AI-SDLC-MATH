"""Manifest `extensions`: mã hợp lệ, burn_s chỉ hữu hạn khi bật burn, nâng cấp net chỉ mua được khi bật net."""

import copy
import json
import os
import tempfile
import unittest

from chonoi.contract import DEFAULT_PATH, enabled, load_contract
from chonoi.errors import BadInput

with open(DEFAULT_PATH, encoding="utf-8") as f:
    BASE = json.load(f)
# nền "tắt hết mở rộng" để kiểm từng mục độc lập với manifest đang dùng
BASE["extensions"] = []
BASE["tuning"]["quan"]["burn_s"] = None


def load_with(**changes):
    c = copy.deepcopy(BASE)
    for key, fn in changes.items():
        fn(c)
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(c, f)
    try:
        return load_contract(path)
    finally:
        os.unlink(path)


class Manifest(unittest.TestCase):
    def test_manifest_dang_bat_burn_va_net(self):
        t = load_contract()["tuning"]
        self.assertEqual(t["extensions"], ["burn", "net"])
        self.assertTrue(enabled(t, "burn") and enabled(t, "net"))
        self.assertFalse(enabled(t, "weapon"))
        self.assertEqual(t["quan"]["burn_s"], 20)

    def test_ma_la_hoac_trung_bi_tu_choi(self):
        for exts in (["bay"], ["net", "net"], "net"):
            with self.assertRaises(BadInput, msg=exts):
                load_with(x=lambda c, e=exts: c.__setitem__("extensions", e))

    def test_burn_s_chi_huu_han_khi_bat_burn(self):
        with self.assertRaises(BadInput):
            load_with(x=lambda c: c["tuning"]["quan"].__setitem__("burn_s", 20))

        def on(c):
            c["extensions"] = ["burn"]
            c["tuning"]["quan"]["burn_s"] = 20
        t = load_with(x=on)["tuning"]
        self.assertTrue(enabled(t, "burn"))
        with self.assertRaises(BadInput):  # bật burn mà burn_s vẫn null
            load_with(x=lambda c: c.__setitem__("extensions", ["burn"]))

    def test_net_mua_duoc_khi_bat(self):
        from chonoi.shop import ShopSim
        for exts, want in (([], "buy_failed"), (["net"], "bought")):
            t = load_with(x=lambda c, e=exts: c.__setitem__("extensions", e))["tuning"]
            ev = []
            ShopSim(t, 1000, 1000, 3.0, {}, []).buy("net", ev)
            self.assertEqual(ev[0][0], want, exts)


if __name__ == "__main__":
    unittest.main()
