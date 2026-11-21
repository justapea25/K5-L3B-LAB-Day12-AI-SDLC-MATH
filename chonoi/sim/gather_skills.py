"""Kỹ năng thêm (sáng tạo của nhóm) cho Gather: giữ F phóng to lưới, giữ G tăng tốc bơi.

TẮT MẶC ĐỊNH: chỉ chạy khi `tuning["skills"]["enabled"]` là true. `game.contract.json` để `false`, nên headless và
test lõi chạy đúng luật gốc; cửa sổ chơi (`chonoi.live`) bật lên (tắt bằng `--no-skills`).

  - net (giữ F):   bán kính bắt cá = net_radius, một lần `catch` bắt tối đa net_max_schools đàn (gần nhất trước).
  - sprint (giữ G): tốc độ bơi nhân sprint_speed_mult.
  - Mỗi kỹ năng đang giữ TRỪ THÊM `*_extra_oxygen_ticks` oxy mỗi tick khi ở dưới nước.
Số liệu chỉ đọc từ tuning["skills"], không hard-code.
"""

NET_BUTTON = "net"
SPRINT_BUTTON = "sprint"


def build(tuning):
    """Cấu hình kỹ năng nếu được bật, ngược lại None (luật lõi)."""
    cfg = tuning.get("skills")
    return cfg if isinstance(cfg, dict) and cfg.get("enabled") is True else None


def begin_step(sim, inp):
    """Đầu mỗi bước: ghi nhận phím đang GIỮ (không phải cạnh lên)."""
    held = getattr(inp, "held", None) or {}
    sim.net_on = sim.skills is not None and bool(held.get(NET_BUTTON))
    sim.sprint_on = sim.skills is not None and bool(held.get(SPRINT_BUTTON))


def speed_factor(sim) -> float:
    return float(sim.skills["sprint_speed_mult"]) if sim.sprint_on else 1.0


def extra_oxygen_drain(sim) -> int:
    """Số tick oxy trừ thêm ở bước này (chỉ gọi khi đang dưới nước)."""
    n = 0
    if sim.net_on:
        n += int(sim.skills["net_extra_oxygen_ticks"])
    if sim.sprint_on:
        n += int(sim.skills["sprint_extra_oxygen_ticks"])
    return n


def catch_radius(sim) -> float:
    return float(sim.skills["net_radius"]) if sim.net_on else float(sim.t["catch_radius"])


def max_catch(sim) -> int:
    return int(sim.skills["net_max_schools"]) if sim.net_on else 1


def annotate(sim, snap):
    """Thêm trạng thái kỹ năng vào snapshot (chỉ khi bật, để headless giữ nguyên schema)."""
    if sim.skills is not None:
        snap["player"]["skills"] = {"net_on": sim.net_on, "sprint_on": sim.sprint_on,
                                    "net_radius": float(sim.skills["net_radius"])}
    return snap
