"""Cửa sổ chơi trực tiếp bằng TRÌNH DUYỆT, chỉ dùng thư viện chuẩn Python.

    python3 -m chonoi.live --mode gather|quan [--seed N] [--port 8000]

Máy chủ HTTP nhỏ (ThreadingHTTPServer) phục vụ `chonoi/web/index.html` và hai API:
    GET  /state  -> snapshot JSON hiện tại (cùng trường như dòng snapshot của headless) + `meta` + `events`
    POST /input  -> {"move": [a, b], "interact": bool, "catch": bool}   (trạng thái phím đang giữ)
    POST /restart -> chơi lại từ đầu (cùng seed, cùng scenario)

Mô phỏng chạy 60 tick/s trong một luồng nền, dùng CÙNG lớp sim như headless (qua `runner.Session`).
Client chỉ ĐỌC snapshot và tự bỏ qua trường chưa có, nên luật do nhóm viết thêm trường nào cũng không vỡ.
Ngẫu nhiên vẫn đi qua `Streams` (seed); chỉ nhịp chạy theo đồng hồ thật, không đi vào luật.
"""

import argparse
import copy
import json
import os
import sys
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .contract import load_contract
from .errors import BadInput
from .inputs import LiveInputs
from .inventory import read_inventory
from .runner import make_session
from .scenario import load_scenario

WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
ART_TYPES = {"/art/" + name: "image/png" for name in
             ("cho-noi.png", "khach.png", "ut-sen-lan.png", "ut-sen-dong.png", "bep-mon.png")}
ART_TYPES.update({"/art/rach-sen.jpg": "image/jpeg", "/art/nha-be.jpg": "image/jpeg",
                  "/art/ca-sau.svg": "image/svg+xml"})
TICK_S = 1.0 / 60.0
MAX_BODY = 4096
RECENT_EVENTS = 40


def demo_tuning(tuning):
    """Chế độ demo (chỉ cửa sổ chơi): ngắn hơn, dễ hơn để trình diễn trọn một Ngày. Headless KHÔNG dùng."""
    t = copy.deepcopy(tuning)
    g, q = t["gather"], t["quan"]
    g["duration_s"] = 120  # 2 phút
    g["oxygen_max_s"] = 60
    q["duration_s"] = 120  # 2 phút
    q["customer_interval_s"] = 8
    q["patience_s"] = 120
    q["interact_radius"] = 2.5
    q["walk_speed"] = 6.0
    for d in t["menu"].values():
        d["cook_s"] = max(1, d["cook_s"] / 2)
    return t


class LiveGame:
    """Một lượt chơi + luồng nền bước 60 tick/s. Mọi truy cập trạng thái đi qua khóa."""

    def __init__(self, mode, tuning, scenario, seed, inventory=None, inventory_out=None, days=1, demo=False):
        self._args = (mode, tuning, scenario, seed, inventory, days, demo)
        self.demo = demo
        self.mode = mode
        self.tuning = tuning
        self.inventory_out = inventory_out
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None
        self._reset()

    def _reset(self):
        self.session = make_session(*self._args)
        self.inputs = LiveInputs()
        self.events = []
        self._saved = False
        self.error = None
        self.stats = {}  # số liệu theo Ngày cho màn Kết quả / Tổng kết (chỉ ở cửa sổ chơi, không vào JSONL)

    # --- luồng nền ----------------------------------------------------------------
    def start(self):
        self._thread = threading.Thread(target=self._loop, name="chonoi-sim", daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _loop(self):
        nxt = time.perf_counter()
        while not self._stop.is_set():
            nxt += TICK_S
            with self._lock:
                try:
                    self._tick_once()
                except Exception:  # luật của nhóm lỗi: báo ra terminal + client, dừng bước (restart để chơi lại)
                    self.error = traceback.format_exc()
                    sys.stderr.write(self.error)
                    self.session.sim.done = True
                    self.session.sim.reason = "error"
            delay = nxt - time.perf_counter()
            if delay > 0:
                self._stop.wait(delay)
            elif delay < -0.25:  # chạy chậm quá thì bỏ bù, tránh chạy dồn
                nxt = time.perf_counter()

    def _tick_once(self):
        s = self.session
        if s.done:
            return
        for row in s.step(self.inputs.advance()):
            self.events.append(row)
            self._count(row)
        del self.events[:-RECENT_EVENTS]
        if s.done and not self._saved:
            self._saved = True
            if self.inventory_out:
                try:
                    s.write_inventory_if_done(self.inventory_out)
                except OSError as e:
                    sys.stderr.write(f"lỗi ghi kho: {e}\n")

    def _count(self, row):
        day = row.get("day", 1)
        st = self.stats.setdefault(day, {"day": day, "served": 0, "left": 0, "no_dish": 0, "money": 0, "tips": 0,
                                         "rep_start": None, "rep_end": None, "dishes": {}, "burnt": 0, "caught": 0,
                                         "gathered": 0, "spoiled": 0})
        name, d = row["name"], row["data"]
        if name == "phase_start" and row["phase"] == "quan":
            st["rep_start"] = self.session.sim.reputation
        elif name == "served":
            st["served"] += 1
            st["dishes"][d["dish_id"]] = st["dishes"].get(d["dish_id"], 0) + 1
        elif name == "paid":
            st["money"] += d.get("amount", 0)
            st["tips"] += d.get("tip", 0)
        elif name == "customer_left" and d.get("reason") == "patience":
            st["left"] += 1
        elif name == "no_dish":
            st["no_dish"] += 1
        elif name == "dish_burnt":
            st["burnt"] += 1
        elif name == "fish_caught":
            st["caught"] += 1
        elif name == "gather":
            st["gathered"] += 1
        elif name == "spoiled":
            st["spoiled"] += 1
        elif name == "quan_end":
            st["rep_end"] = d.get("reputation")

    # --- API cho handler -----------------------------------------------------------
    def state_json(self) -> bytes:
        with self._lock:
            snap = self.session.snapshot()
            view = snap.get("phase", self.mode)
            snap["view"] = view
            snap["meta"] = self.tuning[view]
            snap["menu"] = getattr(self.session.sim, "menu", None)  # quán: món đang bán (day đã lọc theo kế hoạch)
            snap["events"] = list(self.events)
            snap["finished"] = self.session.done
            snap["reason"] = self.session.sim.reason if self.session.done else None
            snap["error"] = self.error
            snap["stats"] = [self.stats[k] for k in sorted(self.stats)]
            snap["demo"] = self.demo
            return json.dumps(snap, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    def set_input(self, body: dict):
        move = body.get("move")
        if move is not None:
            ok = (isinstance(move, list) and len(move) == 2 and
                  all(isinstance(c, (int, float)) and not isinstance(c, bool) and abs(c) <= 1 for c in move))
            if not ok:
                raise ValueError("move phải là [a, b] trong [-1, 1]")
        buttons = {}
        for b in ("interact", "catch", "pause", "shop_done", "net", "sprint"):
            if b in body:
                if not isinstance(body[b], bool):
                    raise ValueError(f"{b} phải là boolean")
                buttons[b] = body[b]
        buy = body.get("buy")
        if buy is not None and not (isinstance(buy, str) and buy):
            raise ValueError("buy phải là chuỗi khác rỗng")
        with self._lock:
            self.inputs.set(move, buy=buy, **buttons)

    def restart(self):
        with self._lock:
            self._reset()

    def skip(self):
        """Phím K (chỉ cửa sổ chơi): sang pha kế bằng đúng luật — sáng: về bến rồi bấm E;
        tối: rút đồng hồ ca còn 1 tick để đóng ca theo luật; Shop: bấm shop_done."""
        with self._lock:
            sess = self.session
            if sess.done:
                return
            sim = sess.sim
            if sim.phase == "gather":
                sim.pos = [float(c) for c in sim.t["dock_pos"]]
                sim.vel = [0.0, 0.0]
                self.inputs.set(interact=False)
                self.inputs.set(interact=True)   # cạnh lên ở tick kế
                self.inputs.set(interact=False)
            elif sim.phase == "quan":
                sim.time_left_ticks = min(sim.time_left_ticks, 1)
            else:
                self.inputs.set(shop_done=False)
                self.inputs.set(shop_done=True)
                self.inputs.set(shop_done=False)


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    game: LiveGame = None  # gán trên lớp con trong make_server

    def log_message(self, fmt, *args):  # yên lặng
        pass

    def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/state":
            self._send(200, self.game.state_json())
        elif path in ART_TYPES:
            try:
                with open(os.path.join(WEB_DIR, path[1:]), "rb") as image:
                    self._send(200, image.read(), ART_TYPES[path])
            except OSError:
                self._send(404, b'{"error":"thieu anh"}')
        elif path in ("/", "/index.html"):
            try:
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                self._send(404, b'{"error":"thieu index.html"}')
        else:
            self._send(404, b'{"error":"khong co"}')

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = -1
        if n < 0 or n > MAX_BODY:
            self._send(400, b'{"error":"body sai"}')
            return
        raw = self.rfile.read(n) if n else b""
        try:
            if path == "/input":
                body = json.loads(raw.decode("utf-8") or "{}")
                if not isinstance(body, dict):
                    raise ValueError("body phải là object")
                self.game.set_input(body)
            elif path == "/restart":
                self.game.restart()
            elif path == "/skip":
                self.game.skip()
            else:
                self._send(404, b'{"error":"khong co"}')
                return
        except (ValueError, UnicodeDecodeError) as e:
            self._send(400, json.dumps({"error": str(e)}).encode("utf-8"))
            return
        self._send(200, b'{"ok":true}')


class LiveServer:
    """Máy chủ + mô phỏng. port=0 -> cổng ngẫu nhiên (đọc `.port`)."""

    def __init__(self, game: LiveGame, host="127.0.0.1", port=8000):
        handler = type("Handler", (_Handler,), {"game": game})
        self.game = game
        self.httpd = ThreadingHTTPServer((host, port), handler)
        self.httpd.daemon_threads = True
        self.host = host
        self.port = self.httpd.server_address[1]
        self._thread = None

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/"

    def start(self):
        self.game.start()
        self._thread = threading.Thread(target=self.httpd.serve_forever, name="chonoi-http", daemon=True)
        self._thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        if self._thread:
            self._thread.join(timeout=2)
        self.game.stop()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="chonoi.live", description="Chơi trực tiếp trên trình duyệt (starter).")
    p.add_argument("--mode", required=True, choices=["gather", "quan", "day"])
    p.add_argument("--days", type=int, default=5, help="chỉ với day: số Ngày (1-5)")
    p.add_argument("--demo", action="store_true",
                   help="chỉ với day: tối nào Má Tư cũng mua thêm đủ nguyên liệu theo kế hoạch để luôn có khách")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--port", type=int, default=8000, help="0 = cổng ngẫu nhiên")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--scenario")
    p.add_argument("--no-skills", dest="no_skills", action="store_true", help="tắt kỹ năng thêm (F lưới, G tăng tốc)")
    p.add_argument("--inventory", help="chỉ với quan: nạp kho từ file")
    p.add_argument("--inventory-out", dest="inventory_out", help="chỉ với gather: ghi kho khi kết thúc buổi")
    a = p.parse_args(argv)
    try:
        if a.inventory and a.mode != "quan":
            raise BadInput("--inventory chỉ dùng với quan")
        if a.inventory_out and a.mode != "gather":
            raise BadInput("--inventory-out chỉ dùng với gather")
        tuning = load_contract()["tuning"]
        if "skills" in tuning and not a.no_skills:
            tuning["skills"]["enabled"] = True  # chỉ cửa sổ chơi; headless đọc contract với enabled=false
        scenario = load_scenario(a.scenario, a.mode, tuning)
        inventory = read_inventory(a.inventory) if a.inventory else None
        if inventory is not None and "stock" in scenario:
            raise BadInput("vừa có quan.stock vừa có --inventory")
        if not 1 <= a.days <= 5:
            raise BadInput("--days phải từ 1 đến 5")
        if a.demo and a.mode != "day":
            raise BadInput("--demo chỉ dùng với --mode day")
        if a.demo:
            tuning = demo_tuning(tuning)
        game = LiveGame(a.mode, tuning, scenario, a.seed, inventory, a.inventory_out, days=a.days, demo=a.demo)
        server = LiveServer(game, a.host, a.port)
    except BadInput as e:
        sys.stderr.write(f"đầu vào sai: {e}\n")
        return 2
    except OSError as e:
        sys.stderr.write(f"không mở được cổng {a.port}: {e}\n")
        return 1
    server.start()
    print(f"Mở trình duyệt tại {server.url}  (chế độ {a.mode}, seed {a.seed}). Ctrl+C để dừng.", flush=True)
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
