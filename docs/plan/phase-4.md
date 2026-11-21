# Kế hoạch Phase 4 (TICKET-04 — Phát hành v1.0.0)

- **Mục tiêu:** contract v1.3 (`bench_cmd`, `soak_cmd`), benchmark có render, soak 10 Ngày, ba cảnh báo dễ nhận biết, chế độ tương phản cao, chạy từ clone sạch trong 3 lệnh, GitHub Release v1.0.0. Tag `phase-4` và Release trước 3:00. Câu hỏi và quyết định: [clarify](../clarify.md) (#24 trở đi).
- **Ghi chú:** PO viết lại sau khi phát hành, đối chiếu `git log` và Release. Tag `phase-4` và `v1.0.0` (annotated, tạo lúc 11:42) cùng trỏ commit `5e188e7` trên `main`.

## Vai và người

| Vai | Việc | Người | Bằng chứng |
|---|---|---|---|
| Release/Integrator | contract v1.3, `chonoi/bench.py`, `chonoi/soak.py`, cảnh báo, tương phản cao, HUD quán, `burn`/`net`, gắn tag, Release v1.0.0 | @justapea25 | `95fcc0d`, `7322434`, Release v1.0.0 (`cho-noi-v1.0.0.zip`) |
| Đóng gói | README "3 lệnh từ clone sạch", LICENSE | @justapea25 | `95fcc0d` |
| Bench/QA | Chạy bench, soak, regression; ma trận `docs/verification/phase-4.md` | @Kaylez-TXL | `docs/proof/phase-4/bench.json`, `soak.json` (còn thiếu ma trận) |
| Điều phối retro | Rà hành động P2, tổng hợp đóng góp trong `docs/retro.md` | @minhthu27 | (còn thiếu) |
| PO | plan Phase 3–4, clarify #18–28, AGENTS.md, CREDITS, README | @linkiewinkie | nhánh `linkiewinkie/docs-phase-3-4` |
| Sáng tạo (sau tag) | Kỹ năng F/G (@LETHESHIYING); tranh chibi, cảnh quán (@Kaylez-TXL); âm thanh, phụ đề SFX, chế độ demo, màn Kết quả Ngày (@justapea25) | nhiều người | `f56e38a`, `d6ce2e9`, `b63b38d`, `cc35d72`, `5a75edd` |

Các commit sáng tạo ở dòng cuối được gộp **sau** tag `phase-4`, nên không nằm trong bản v1.0.0 (release notes ghi "chưa có âm thanh/phụ đề SFX", đúng với tag).

## Tiêu chí chấp nhận (AC-P4-xx, nhóm tự đánh theo TICKET-04)

| AC | Nội dung | Nguồn | Kiểm bằng |
|---|---|---|---|
| AC-P4-01 | `contract_version: "1.3"`, `bench_cmd` và `soak_cmd` ở gốc `game.contract.json`; gameplay, tuning, kho, JSONL giữ v1.2 | 1 | `test_phase4.test_manifest_v13` |
| AC-P4-02 | `<bench_cmd> --seed 42 --duration 30 --out bench.json`: cảnh sáng lõi (độ tươi, cá bơi, Cá Sấu, hiệu ứng mặc định), Út Sen đứng yên ở bến, 1280×720, làm nóng 3 s rồi đo | 1 | `test_phase4.test_bench_json` |
| AC-P4-03 | `bench.json` đúng 5 trường: `frames`, `measured_s`, `avg_fps = frames / measured_s`, `p1_low_fps` (nghịch đảo thời gian trung bình của `max(1, ceil(0.01 × frames))` khung chậm nhất), `load_ms` | 1 | `test_bench_json`; `docs/proof/phase-4/bench.json` |
| AC-P4-04 | Báo cáo mốc avg ≥ 60 FPS, 1% low ≥ 30 FPS, load ≤ 10 s (không chấm); artifact từ commit nộp | 1 | `bench.json`: avg 2234.86, 1% low 876.61, load 23 ms |
| AC-P4-05 | `<soak_cmd> --seed 7 --days 10 --out soak.json`: 10 Ngày trong một tiến trình, mỗi Ngày gather → quan → shop, kế hoạch D1–D5 lặp; tiền, earned, uy tín, cấp, id cá thể tiếp tục | 2 | `test_phase4.test_soak_json_va_tat_dinh` |
| AC-P4-06 | `soak.json` có `days`, `days_completed`, `crashes`, `results[{day, earned, reputation, score}]`, `duration_s`; đạt khi `days_completed = days` và `crashes = 0`; tất định khi bỏ `duration_s`; không ghi bảng xếp hạng | 2 | `test_soak_json_va_tat_dinh`; `docs/proof/phase-4/soak.json` (10/10, 0 crash) |
| AC-P4-07 | Cảnh báo bằng chữ hoặc biểu tượng: thủy quái gần, oxy sắp hết, khách sắp giận | 1 | Chơi thử, ảnh chụp trong `docs/proof/phase-4/` |
| AC-P4-08 | Chế độ tương phản cao (phím H hoặc `?contrast=high`); chơi thử cả ba cảnh báo ở chế độ đó | 1 | Chơi thử, ảnh chụp ba cảnh báo ở tương phản cao |
| AC-P4-09 | Từ clone sạch chạy được bản có giao diện trong ≤ 3 lệnh trên macOS/Linux; README ghi yêu cầu môi trường, điều khiển, lệnh test, headless, bench | 1 | README mục "Chạy game (v1.0.0)"; log thử clone sạch |
| AC-P4-10 | GitHub Release v1.0.0 có bản đóng gói chạy được; release notes nêu điểm mới, cách chạy, giới hạn đã biết | 1 | Release v1.0.0, asset `cho-noi-v1.0.0.zip` |
| AC-P4-11 | `CHANGELOG.md` theo từng phase; `CREDITS.md` và `LICENSE` rà đủ tài sản đã dùng | 1 | `CHANGELOG.md`, `CREDITS.md`, `LICENSE` |
| AC-P4-12 | Regression P1–P3 còn hiệu lực đạt trên commit bàn giao | DoD | `unittest` trên `phase-4` |
| AC-P4-13 | Tag `phase-4` và Release v1.0.0 cùng trỏ tới một commit trên `main`, trước 3:00 | DoD | `git rev-parse phase-4^{commit} v1.0.0^{commit}` → cùng `5e188e7` |
| AC-P4-14 | `docs/verification/phase-4.md` và bằng chứng khớp commit tag; clarify, nhật ký AI cập nhật | DoD | QA, PO |
| AC-P4-15 | Retro rà hành động P2 và chốt việc tiếp theo, nêu một lỗi AI và cách xác minh; mỗi người có `docs/members/<handle>.md` (≤ 200 từ) | 4, DoD | `docs/retro.md`, `docs/members/` |
| AC-P4-16 | (Mở rộng, nếu tính) Phụ đề SFX: phụ đề cho mọi hiệu ứng âm thanh, chơi thử khi tắt tiếng | 3 | Chơi thử với phím N (sau tag `phase-4`) |

Không làm: bảng xếp hạng cục bộ (`leaderboard`).

## Việc còn mở (PO theo dõi)

- AC-P4-07, 08, 09: chưa có ảnh chụp cảnh báo và log thử clone sạch trong `docs/proof/phase-4/`.
- AC-P4-14, 15: chưa có `docs/verification/phase-4.md`, `docs/retro.md` còn trống, thiếu `docs/members/minhthu27.md` và `docs/members/viethoang127.md`.
