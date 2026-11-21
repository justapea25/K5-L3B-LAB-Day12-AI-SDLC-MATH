# Changelog

## [1.0.0] — Phase 4 (Test Contract v1.3)
### Added
- `bench_cmd` (`python3 -m chonoi.bench`): benchmark có render 1280×720, cảnh sáng lõi seed 42, làm nóng 3 s, xuất `bench.json`
  {avg_fps, p1_low_fps, frames, measured_s, load_ms}. Kết quả trên máy dev: `docs/proof/phase-4/bench.json`.
- `soak_cmd` (`python3 -m chonoi.soak`): N Ngày trong một tiến trình bằng bot tất định, kế hoạch D1–D5 lặp; `soak.json`
  {days, days_completed, crashes, results[], duration_s}. 10 Ngày: 10/10, 0 crash (`docs/proof/phase-4/soak.json`).
- Cảnh báo dễ nhận biết: 🐊 Thủy quái! (+ viền tím), 🫧 Oxy sắp hết! / Hết hơi!, 😠 Khách sắp giận! (kèm số bàn).
- Chế độ tương phản cao (phím H hoặc `?contrast=high`, nhớ lựa chọn).
- HUD quán: khách kế tiếp, bàn trống, món nấu được từ kho, giải thích khi khách bỏ về vì `no_dish`; HUD sáng: "Cần lấy" theo kế hoạch.
- Shop: phím 3 mua Vợt hút cá. README chạy được trong 3 lệnh; LICENSE.
### Changed
- `contract_version: "1.3"`, khai `bench_cmd`, `soak_cmd`; `run_cmd` chạy `--mode day`. Gameplay/kho/JSONL giữ v1.2.

## Phase 1 (Test Contract v1.0)
- Lõi gather (oxy, ngạt, Máu, ngất, giỏ LIFO, hái, bắt cá, cập bến), quán (khách, giữ chỗ, bếp, bưng, trả tiền, boa, uy tín),
  bàn giao kho gather → quan qua file.

## Unreleased (lịch sử chi tiết Phase 2–3)

### ⚠️ Breaking change — Contract v1.2 (Phase 3, "Mùa Nước Nổi")
- **Kho đếm → kho cá thể.** File kho, `gather.hold`, `quan.stock`, snapshot `hold`/`stock` (quán và Shop):
  `{"items":[{"id":"I1","kind":"ca_linh","fresh":100}]}`. Kho rỗng `{"items":[]}`. File kho đếm cũ, id trùng,
  kind lạ, fresh ngoài [0,100] → **mã 2**. File ghi theo id, fresh đủ chữ số để đọc lại y nguyên.
- `customers[].reserved` là **mảng id cá thể** (bỏ trống thì tự cấp: tươi nhất, hòa theo id).
- `lost` trong `monster_hit`/`faint` là mảng cá thể theo thứ tự bỏ (LIFO). `cook_started.data.items` là cá thể đã tiêu (sắp kind rồi id).
- `base_price` chốt lúc bắt đầu nấu = floor(giá niêm yết × trung bình fresh / 100); boa tính trên giá đã chốt.
- `contract_version: "1.2"`, thêm `tuning.freshness {initial:100, gather_decay_per_s:0.5, quan_decay_per_s:0.25, spoiled_below:30}`.

### Added (Phase 3)
- Độ tươi: giỏ −0.5/s, kho quán −0.25/s (kể cả hàng đang giữ), pause dừng hao; tính nội bộ 240 đơn vị/điểm để chính xác ở ngưỡng 30.
- Event `spoiled {item_id, kind, location: hold|stock}` đúng một lần khi đi từ ≥ 30 xuống < 30, theo id.
- Giữ chỗ theo id; phần giữ vừa ươn → nhả và thử giữ lại một lần (order_tick rồi id bàn), thiếu → `unfulfillable`.
- Id cá thể I1, I2… tăng xuyên pha và Ngày; Ngày kế cấp id mới cho mẫu `gather.hold`.
- HUD: thanh độ tươi dưới từng ô giỏ, gạch chéo hàng ươn; kho ghi độ tươi thấp nhất và số hàng ươn.
- `tests/test_phase3.py`.

### Cách cập nhật fixture cũ
- `tests/helpers.py`: `migrate_scenario` (tự áp trong `write_json`) đổi `hold` list kind / `stock` dict đếm sang mảng cá thể
  (id I1… theo thứ tự), `reserved` theo lượng → bỏ để hệ thống tự cấp. Hàm `kinds()`, `counts()`, `same_items()` để so kết quả.
- Test đổi kỳ vọng vì luật mới: giá món 60 → 59 (cá đã hao 1 tick ở quán lúc nấu), JSONL làm tròn 3 chữ số nên so kho có dung sai ±0.01.

### Added (Phase 2, v1.1)
- Contract v1.1, cá bơi/sinh, Cá Sấu, chế độ `day` (`--days 1-5`), Shop, pause ở mọi mode; cửa sổ chơi có `--mode day`.
### Added
- Quán lát 4 (@minhthu27): `quan_service.py` — `tick_service` (bếp nấu -> `dish_ready`, khách ăn đếm ngược), `interact` (bếp trước bàn: `cook_started` / `dish_picked` / `served`), `settle` (`paid`, boa, uy tín, rời bàn; hết ca trả hết rồi `quan_end`).
- `tests/test_quan_service.py`: 8 test hộp đen (nấu đến trả tiền, thiếu nguyên liệu, đơn unfulfillable, không boa, phục vụ nhầm khách, hết ca, cùng seed).
### Changed
- Ghép lát 4 với `quan_customers` (lát 3): dùng `build_fixture_customers`, `remove_customer`, `phase_tick`; món ở bếp và trên tay là payload `{order_id, dish_id, base_price}`.
- Sự kiện lát 4 đổi theo PRD/QA: `served` `{order_id, table_id, dish_id, patience_ticks_left, base_price, tip}`, `paid` `{order_id, table_id, base_price, tip, amount, reason}`, `cook_started`/`dish_ready`/`dish_picked` `{stove_id, order_id, dish_id}`.
- `quan.py`: thứ tự bước theo `docs/contracts/customer.md` mục 5; khách scenario có mặc định và `reserved` cấp theo công thức; `hand` là `{order_id, dish_id, base_price}`.
