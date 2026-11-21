# Nhật ký dùng AI (theo phase và theo người)

> Mỗi người ghi vào **mục của mình** (tránh conflict). Thêm dòng ở cuối bảng của mình.

## justapea25

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Claude Opus 5.5) | Code gather lát 1 (oxy, ngạt, Máu, ngất, `_add_to_hold`) + 9 test | chưa đo | Test reset bộ đếm ngạt bị đỏ: AI dựng scenario ở mặt nước với `zero_oxy_ticks > 0`, bị scenario từ chối (mã 2); sửa thành bắt đầu ngay dưới mặt nước rồi bơi lên. Tôi đọc lại luật và chạy toàn bộ test (41 OK) trước khi gộp |
| 1 | Claude Code (Claude Opus 5.5) | Dựng khung lát 2–4 (tách file, nối lời gọi), hợp đồng khách/sự kiện | chưa đo | Lần đầu AI ghi tên người vào docstring/TODO; tôi yêu cầu chỉ ghi theo lát |
| 2 | Claude Code (Claude Opus 5.5) | Contract v1.1 (day_plan tính từ công thức), cá bơi/sinh, Cá Sấu, `day`, Shop, pause | chưa đo | AI để payload `faint`/`oxygen_empty`/`hold_full` theo giả định; test QA đối chiếu PRD-0 bắt được, tôi sửa theo PRD (#8). Test cũ nút `attack`, mode `day` đổi có ghi lý do |
| 3 | Claude Code (Claude Opus 5.5) | Kho cá thể v1.2 (240 đơn vị/điểm tươi), giữ chỗ theo id, giá theo tươi, chuyển fixture cũ; mở rộng burn/net | chưa đo | `scenario.py` truyền kho dạng ngoài vào hàm cần dạng nội bộ (`KeyError: units`); lộ ra khi chạy test hộp đen, tôi sửa chỗ chuyển đổi. Kỳ vọng test bắt cá sai bán kính lõi, tôi đối chiếu luật rồi sửa test |
| 4 | Claude Code (Claude Opus 5.5) | bench/soak, cảnh báo + tương phản cao, Release v1.0.0; sau tag: UI, demo, âm thanh + phụ đề, Cá Sấu SVG | chưa đo | AI chèn khối chỉ dẫn quán nhầm vào màn lặn và để tên món hiện `[object Object]`; tôi phát hiện bằng ảnh chụp Chrome headless. Bench đầu tiên lệch `avg_fps` do làm tròn, sửa theo đúng định nghĩa đề |

## LETHESHIYING

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Claude Sonnet 5.5) | Đọc repo, phân tích phần việc; code gather lát 2 (`try_gather`, `try_catch`) + 16 test hộp đen | chưa đo | 2 test đầu bị đỏ do AI viết sai test, không phải sai luật: (1) scenario đặt cá ở mặt nước bị headless từ chối (mã 2, cá phải ở dưới nước); (2) test hồi chiêu lệch 1 tick vì bấm hai lần liên tiếp không có frame thả nút nên không có cạnh lên. Tôi đọc lỗi, sửa test, chạy lại toàn bộ (57 OK) trước khi đẩy |
| 1 | Claude Code (Claude Sonnet 5.5) | Soạn giả định gửi PO, điền TEAM/members/nhật ký | chưa đo | AI đưa tên hiển thị tạm là handle vì không biết họ tên thật; tôi cần tự thay |
| 2 | Claude Code (Claude Sonnet 5.5) | Giải quyết conflict khi merge `main`; sửa `gather`, `fish_caught`, `hold_full` theo PRD-0 | chưa đo | AI tự đặt tên trường sự kiện (`count`, `hold_count`) khác PRD-0 (`amount`, `yield`, `hold_full {action, id, required, free}`); phát hiện vì test tích hợp của QA đỏ sau khi merge `main`. Sửa và chạy lại toàn bộ test trước khi đẩy |
| 3–4 | Claude Code (Claude Sonnet 5.5) | Kỹ năng thêm: giữ F lưới lớn, giữ G tăng tốc (`gather_skills.py`, 17 test), nối `live.py`/`index.html`; điều tra lỗi giỏ và bắt cá | chưa đo | Lần đầu script thay thế file không khớp vì file dùng CRLF; test dựng giỏ thiếu trường `fresh` bị headless từ chối. Điều tra "giỏ lỗi / không bắt được cá": chạy 100 ván ngẫu nhiên và thử qua server live, không tái hiện được lỗi logic; AI chỉ nêu nguyên nhân khả dĩ (hồi chiêu nuốt phím, cá linh cần đủ 3 chỗ, bộ gõ Telex), tôi tự thử lại trên game |

## viethoang126

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|

## minhthu27

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Sonnet 5.5) | Viết `quan_service.py`, test lát 4, docs Scrum | chưa đo | Lần đầu viết khi chưa có khung của Lead nên dùng thêm state `assigned`/`left` ngoài hợp đồng khách; sửa lại sau khi rebase; sau đó schema khách đổi tên trường (`dish`→`dish_id`...) nên phải viết lại một lượt |
| 2 | Claude Code (Sonnet 5.5) | Ghép lát 4 với `quan_customers` (lát 3) và contract v1.1: payload món ở bếp/tay, `served`/`paid` theo test QA | chưa đo | Lần đầu AI đoán tên trường sự kiện (`customer_id`, `dish`); test QA đọc PRD cho tên khác (`order_id`, `dish_id`, `amount`) nên phải sửa. Một test của tôi dùng `reserved={}` cho đơn `reserved` bị kiểm khách dựng sẵn từ chối (mã 2), phải đổi fixture |
| 3–4 | Claude Code (Sonnet 5.5) | Chẩn đoán "game quán không có khách" (menu lọc theo kế hoạch Ngày, kho phải đủ nguyên liệu), viết hướng dẫn chơi, điền TEAM/members/retro/standup | chưa đo | AI không mở được link game của người khác nên không xác nhận được cấu hình; chỉ kết luận từ code và chạy headless |

## Kaylez-TXL

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Codex | Đối chiếu PRD-0 mục E–G, viết test hộp đen, chạy test trên `origin/main` và nhánh luật, điền ma trận và lưu log | Chưa đo | Bản đầu điền handle thay cho họ tên trong `TEAM.md`. Đã sửa theo thông tin thành viên cung cấp và giữ các biểu mẫu báo cáo. |

## linkiewinkie

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Codex | Bản nháp kế hoạch, TEAM, clarify, ma trận kiểm chứng và lệnh lưu bằng chứng | Chưa đo | Sửa cả file của người khác (dòng TEAM của 4 bạn, ma trận và bằng chứng của QA, standup). Tôi bỏ các phần đó khỏi nhánh và chuyển bản ma trận, bằng chứng cho QA. Trên Windows, lệnh đầu đọc stderr sai mã trang, phải bật UTF-8 cho tiến trình test. |
| 1 | Claude Code (Claude Opus 5.5) | Đối chiếu PRD-0 với contract, chốt clarify, AC-P1-xx trong plan, AGENTS.md, 2 skill, README, CREDITS | Chưa đo | Không đọc được PRD-0 trên lab board (mở theo giờ, cần đăng nhập) nên tôi dán PRD vào. AI phát hiện `events.md` và `customer.md` lệch tên trường so với PRD-0 mục D/E; tôi chốt theo PRD. |
| 2 | Claude Code (Claude Opus 5.5) | Plan Phase 2 (AC-P2-01..25), clarify #8–17, AGENTS.md v1.1, skill `check-contract` (script so số chuẩn v1.1), cập nhật `run-tests`, README | Chưa đo | AI đề xuất chia người cho 4 lát; tôi để Lead chia. Script ban đầu ép `fish_weights` = 0.4/0.3/0.3 và `recoil_dist` = 2.0 trong khi ticket không ghi đơn vị → đổi sang kiểm tỷ lệ/có mặt. Lỗi in tiếng Việt trên console Windows (cp1252) → ép UTF-8. Tự kiểm: contract chuẩn dựng từ bảng ticket cho 0 lỗi. |
| 3–4 | Claude Code (Claude Opus 5.5) | Rà docs còn thiếu; plan Phase 3–4 (AC-P3-01..17, AC-P4-01..16, bảng tác động đổi schema kho); clarify #18–28; AGENTS.md, CREDITS, README, nâng `check-contract` lên v1.3, thêm smoke v1.2/v1.3 vào `run-tests`; sửa `python3` trên Windows | Chưa đo | (1) Tôi chuyển nhánh giữa phiên, AI vẫn kết luận theo nhánh cũ "game mới ở Phase 2"; phát hiện khi AI đọc `git log` thấy commit Phase 4. (2) AI ghi tag `phase-4` và `v1.0.0` trỏ hai commit khác nhau vì lấy mã đối tượng tag; kiểm `rev-parse <tag>^{commit}` thì cùng `5e188e7`. (3) Clarify `net` lần đầu ghi "gần nhất trước"; đọc code thấy duyệt theo id nên sửa. (4) README ghi demo/Kết quả Ngày thuộc Phase 4; kiểm `merge-base --is-ancestor` thì gộp sau tag. Script `check-contract` mới: thử với một contract cài 4 lỗi, bắt đủ 4. |
