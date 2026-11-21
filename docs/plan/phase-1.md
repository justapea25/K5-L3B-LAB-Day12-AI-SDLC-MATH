# Kế hoạch Phase 1

**Mục tiêu:** chơi được buổi sáng (gather) và buổi tối (quan) đúng lõi PRD-0, hai tiến trình headless nối nhau qua file kho theo Test Contract v1.0. Tag `phase-1` trên `main` trước 1:00. Câu hỏi và quyết định: [clarify](../clarify.md).

## Việc / người / phụ thuộc

| Phần việc | Người | File | Phụ thuộc, bàn giao | AC |
|---|---|---|---|---|
| Lát 1 — oxy, ngạt, Máu, ngất, dive/surface, giỏ LIFO | @justapea25 | `sim/gather.py` | Push `_add_to_hold` trước; sửa contract theo [clarify #3, #7](../clarify.md) | 05–08 |
| Lát 2 — hái, mọc lại, bắt cá, hồi chiêu, `hold_full` | @LETHESHIYING | `sim/gather_harvest.py` | Cần helper giỏ (đã đổi tham số theo clarify #3) | 10–13 |
| Lát 3 — khách đến, chọn món, giữ chỗ, kiên nhẫn, bỏ đi, `no_dish` | @viethoang127 | `sim/quan_customers.py`, `scenario.py` | Chốt schema khách theo [clarify #7](../clarify.md) trước để lát 4 code; làm trọn việc khách rời ([clarify #6](../clarify.md)) | 15, 16, 20 |
| Lát 4 — bếp, bưng, phục vụ, tiền, boa, uy tín, `quan_end` | @minhthu27 | `sim/quan.py`, `sim/quan_service.py` | Dùng schema khách của lát 3 | 17–20 |
| QA — test hộp đen theo AC, tích hợp, verification | @Kaylez-TXL | `tests/test_integration.py`, `docs/verification/`, `docs/proof/` | Chạy trên commit tích hợp | 01–04, 09, 14, 21 |
| PO, harness AI, docs | @linkiewinkie | `docs/clarify.md`, `docs/plan/`, `AGENTS.md`, `.agents/skills/`, `README.md`, `CREDITS.md` | Trả lời câu hỏi PRD trong clarify | 23 |
| Contract, gộp, tag | @justapea25 | `game.contract.json`, `docs/contracts/` | Gộp helper/schema trước | 22 |

## Tiêu chí chấp nhận (AC-P1-xx, nhóm tự đánh theo PRD-0)

| AC | Nội dung | Nguồn |
|---|---|---|
| AC-P1-01 | Headless nhận đủ cờ; mã 0 / 1 / 2 đúng; kiểm tra dữ liệu trước khi ghi JSONL hay kho | B |
| AC-P1-02 | JSONL: snapshot ở tick 0, mỗi `--snapshot-every`, tick dừng; event trước snapshot; `end` là dòng cuối; `score = earned + 100 × floor(reputation)` | E |
| AC-P1-03 | Cùng seed và đầu vào → JSONL và file kho giống từng byte | E |
| AC-P1-04 | Vận tốc hội tụ trong ≤ `ramp_max_ticks`, chặn biên, hướng theo `move` khác 0 gần nhất | F |
| AC-P1-05 | Oxy: mặt nước (d ≤ 0.5) +6 kẹp max, dưới nước −1 kẹp 0; `oxygen_empty` khi từ dương xuống 0 | F |
| AC-P1-06 | Ngạt: tính cả tick chạm 0; đủ 60 → −1 Máu, `choke`; nổi lên reset đếm | F |
| AC-P1-07 | Ngất: Máu 0 → bỏ giỏ LIFO, `faint`, `gather_end fainted`, kho rỗng | F, G |
| AC-P1-08 | `dive` / `surface` chỉ khi đổi phía biên mặt nước, `data.pos` sau di chuyển | E |
| AC-P1-09 | Cạnh `interact` trong bán kính bến (tính cả mép) → `gather_end docked`, xét bến trước hái | F |
| AC-P1-10 | Hái: chỉ ở mặt nước, nút ready gần nhất hòa theo id, +1, `regrow_ticks = regrow_s × 60`, event `gather`; thiếu chỗ → `hold_full`, nút giữ nguyên | F |
| AC-P1-11 | `regrow_ticks` từ 1 về 0 phát `node_regrown`, hái được ngay | F |
| AC-P1-12 | Bắt cá: dưới nước, hết hồi, đàn gần nhất hòa theo id, thêm đủ yield, xóa đàn, `fish_caught`, đặt cooldown; thiếu chỗ → `hold_full`, giữ đàn và cooldown; không có đàn → không event, không hồi chiêu | F |
| AC-P1-13 | Hết giờ → `gather_end time` ở mọi độ sâu, giữ giỏ; hái/bắt hợp lệ ở bước cuối vẫn vào kho | F |
| AC-P1-14 | File kho: ghi đúng một lần khi `gather_end`, ghi nguyên tử; chạm `--ticks` trước khi xong thì không ghi; bên đọc từ chối sai schema (mã 2) | G |
| AC-P1-15 | Lượt khách ở `first_customer_tick` rồi mỗi `customer_interval_s`; bàn trống id nhỏ nhất; chọn đều theo seed trong món đủ kho khả dụng; giữ chỗ ngay; `customer_arrived` hoặc `no_dish` | F |
| AC-P1-16 | Kiên nhẫn giảm từ bước sau; về 0 khi còn giờ → rời, uy tín + `left_reputation_delta`, nhả giữ chỗ, bỏ món, `customer_left patience` | F |
| AC-P1-17 | Bếp idle lấy đơn reserved cũ nhất (`order_tick`, rồi id bàn), tiêu nguyên liệu giữ, `cook_started`; nấu xong → ready, `dish_ready` | F |
| AC-P1-18 | Bếp ready → tay trống, `dish_picked`; phục vụ đúng `order_id` → `served`, khách ăn; boa = floor(giá × `tip_rate`) nếu tỷ lệ kiên nhẫn ≥ `tip_min_patience_ratio` | F |
| AC-P1-19 | Ăn xong → `paid finished_eating`, cộng `money` / `earned`; boa dương + `tip_reputation`, kẹp uy tín | F |
| AC-P1-20 | Hết ca: khách đang ăn trả ngay (`closing`), khách chờ rời `closing` không trừ uy tín, rồi `quan_end` | F |
| AC-P1-21 | Smoke hai tiến trình (seed 42, `dock.json`): snapshot quán tick 0 có `stock {"bong_sung":2,"ca_loc":1}` | G |
| AC-P1-22 | `game.contract.json` đủ khóa mục A, số trong dải hợp lệ, `team_size` = 6 | A |
| AC-P1-23 | README chạy từ clone sạch ≤ 3 lệnh, có điều khiển, cách tính điểm, lệnh test; TEAM đủ người; verification và proof ở commit tag; HUD đọc được khi chơi | DoD |

## Rủi ro

- **Contract lệch PRD-0** (`events.md`, `customer.md`): test ẩn so đúng tên trường. Lead sửa contract trước khi lát 2–4 code xong ([clarify #3, #7](../clarify.md)).
- **Lát 3 và lát 4 phụ thuộc nhau** qua schema khách và phần giữ chỗ: lát 3 chốt schema trước, QA test luồng khách–bếp trên commit tích hợp.
- **Mở rộng:** nhóm 6 người phải làm ≥ 2 mục mở rộng trong cả buổi lab. Phase 1 làm lõi trước, chọn mục ở Phase 2.
- **Môi trường Windows:** `headless_cmd` gọi `python3`; máy không có `python3` trên PATH thì test hộp đen lỗi. Xem lệnh trong [AGENTS.md](../../AGENTS.md).
