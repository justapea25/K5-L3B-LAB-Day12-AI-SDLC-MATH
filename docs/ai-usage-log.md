# Nhật ký dùng AI (theo phase và theo người)

> Mỗi người ghi vào **mục của mình** (tránh conflict). Thêm dòng ở cuối bảng của mình.

## justapea25

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Claude Opus 5.5) | Code gather lát 1 (oxy, ngạt, Máu, ngất, `_add_to_hold`) + 9 test | chưa đo | Test reset bộ đếm ngạt bị đỏ: AI dựng scenario ở mặt nước với `zero_oxy_ticks > 0`, bị scenario từ chối (mã 2); sửa thành bắt đầu ngay dưới mặt nước rồi bơi lên. Tôi đọc lại luật và chạy toàn bộ test (41 OK) trước khi gộp |
| 1 | Claude Code (Claude Opus 5.5) | Dựng khung lát 2–4 (tách file, nối lời gọi), hợp đồng khách/sự kiện | chưa đo | Lần đầu AI ghi tên người vào docstring/TODO; tôi yêu cầu chỉ ghi theo lát |

## LETHESHIYING

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Claude Sonnet 5.5) | Đọc repo, phân tích phần việc; code gather lát 2 (`try_gather`, `try_catch`) + 16 test hộp đen | chưa đo | 2 test đầu bị đỏ do AI viết sai test, không phải sai luật: (1) scenario đặt cá ở mặt nước bị headless từ chối (mã 2, cá phải ở dưới nước); (2) test hồi chiêu lệch 1 tick vì bấm hai lần liên tiếp không có frame thả nút nên không có cạnh lên. Tôi đọc lỗi, sửa test, chạy lại toàn bộ (57 OK) trước khi đẩy |
| 1 | Claude Code (Claude Sonnet 5.5) | Soạn giả định gửi PO, điền TEAM/members/nhật ký | chưa đo | AI đưa tên hiển thị tạm là handle vì không biết họ tên thật; tôi cần tự thay |

## viethoang126

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|

## minhthu27

| Phase | Công cụ / model | Việc | Token / chi phí ước tính | Ghi chú (AI sai ở đâu?) |
|---|---|---|---|---|
| 1 | Claude Code (Sonnet 5.5) | Viết `quan_service.py`, test lát 4, docs Scrum | (điền) | Lần đầu viết khi chưa có khung của Lead nên dùng thêm state `assigned`/`left` ngoài hợp đồng khách; sửa lại sau khi rebase; sau đó schema khách đổi tên trường (`dish`→`dish_id`...) nên phải viết lại một lượt |

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
