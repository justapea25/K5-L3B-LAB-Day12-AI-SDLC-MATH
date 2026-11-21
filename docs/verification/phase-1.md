# Ma trận truy vết Phase 1

2026-11-21 · tag `phase-1` · commit `b055dfe` · Python 3.13.17 · Windows 11

Tiêu chí theo [kế hoạch Phase 1](../plan/phase-1.md). Kết quả bên dưới ghi phạm vi của từng ca kiểm.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P1-01 | CLI và phân loại lỗi qua `test_smoke_p1.Contract` | [Unittest](../proof/phase-1/unittest-tag.txt) | Một phần. Đã thử 0 và 2, chưa kiểm đủ mã 1 và mọi trường hợp không ghi file. |
| AC-P1-02 | Snapshot tick 0/tick dừng và dòng end qua `test_con_01_ticks_zero_and_end_line` | [Unittest](../proof/phase-1/unittest-tag.txt) | Một phần. Chưa kiểm đủ thứ tự event và công thức điểm. |
| AC-P1-03 | `test_con_02_deterministic_bytes`, `test_dock_o_buoc_cuoi_va_kho_tat_dinh` và so byte JSONL hai chế độ | [Unittest](../proof/phase-1/unittest-tag.txt) · [Tính tất định](../proof/phase-1/determinism.txt) | Đạt. |
| AC-P1-04 | `test_smoke_p1.Movement` kiểm gia tốc, hướng và mép bản đồ | [Unittest](../proof/phase-1/unittest-tag.txt) | Đạt trong các ca đã chạy. |
| AC-P1-05 | `test_gather_oxy.Oxygen` và kiểm payload `test_oxygen_empty_co_payload_theo_contract` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Event có `pos` thay cho `oxygen_ticks`. |
| AC-P1-06 | `test_gather_oxy.Choke` kiểm chu kỳ trừ Máu và reset khi nổi | [Unittest](../proof/phase-1/unittest-tag.txt) | Đạt trong các ca đã chạy. |
| AC-P1-07 | `test_ngat_bo_gio_theo_lifo_va_xuat_kho_rong` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. File kho rỗng qua test lát 1, payload `faint` lệch schema. |
| AC-P1-08 | `test_dive_roi_surface` kiểm cả hai chiều qua biên mặt nước | [Unittest](../proof/phase-1/unittest-tag.txt) | Một phần. Có hai event, chưa xác nhận đủ dữ liệu vị trí. |
| AC-P1-09 | `test_dock_o_buoc_cuoi_va_kho_tat_dinh` và smoke tại bến | [Unittest](../proof/phase-1/unittest-tag.txt) · [Smoke](../proof/phase-1/smoke.txt) | Một phần. Đã kiểm cập bến, chưa kiểm riêng ưu tiên trong bán kính. |
| AC-P1-10 | Hái nút gần nhất, hòa theo ID và thiếu chỗ | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa kiểm chứng đầy đủ. Ca hái nút vừa mọc lại không phát `gather`. |
| AC-P1-11 | `test_hai_nut_vua_moc_lai_o_buoc_cuoi_roi_chuyen_kho` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Có `node_regrown` nhưng thiếu `gather`. |
| AC-P1-12 | Ca bắt cá bước cuối và ca không đủ chỗ | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Thiếu `fish_caught` và `hold_full`. |
| AC-P1-13 | `test_time_ends_gather_and_keeps_hold` và hái/bắt ở bước cuối | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt đầy đủ. Hết giờ giữ giỏ, ca hái/bắt ở bước cuối thất bại. |
| AC-P1-14 | `test_smoke_p1.Integration` và smoke giao kho | [Unittest](../proof/phase-1/unittest-tag.txt) · [Smoke](../proof/phase-1/smoke.txt) | Một phần. Ghi/đọc và ca tick limit qua test, chưa xác minh thao tác thay thế nguyên tử. |
| AC-P1-15 | `test_quan_goi_mon_theo_kho_va_lich_khach` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Thiếu `customer_arrived` và `no_dish`. |
| AC-P1-16 | Khách hết kiên nhẫn, nhả giữ chỗ và bỏ món | — | Chưa kiểm chứng. |
| AC-P1-17 | Nhận đơn, tiêu nguyên liệu và nấu xong | — | Chưa kiểm chứng. |
| AC-P1-18 | `test_quan_phuc_vu_o_tick_het_kien_nhan_va_dong_ca` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Thiếu `served` ở bước thử. |
| AC-P1-19 | Trả tiền sau khi ăn xong và cập nhật uy tín | — | Chưa kiểm chứng. |
| AC-P1-20 | `test_quan_phuc_vu_o_tick_het_kien_nhan_va_dong_ca` | [Unittest](../proof/phase-1/unittest-tag.txt) | Chưa đạt. Có `quan_end` nhưng thiếu `paid` ở bước thử. |
| AC-P1-21 | Smoke hai tiến trình, seed 42, tick 0 của quán | [Smoke](../proof/phase-1/smoke.txt) | Đạt. Stock có 2 bông súng và 1 cá lóc. |
| AC-P1-22 | Khóa và số chuẩn contract v1.0 | — | Chưa kiểm chứng toàn bộ. |
| AC-P1-23 | `test_live` và kiểm trạng thái hồ sơ qua tag | [Unittest](../proof/phase-1/unittest-tag.txt) · [Hồ sơ sơ bộ](../proof/phase-1/qa-headless.md) | Một phần. HTTP qua test. Chưa có bằng chứng chơi thử hai buổi và hồ sơ tại tag còn ở trạng thái sơ bộ. |

## Đánh giá ngắn

Unittest chạy 50 test và báo 8 lỗi assertion, trong đó có 2 lỗi ở các ca con của cùng một test. Smoke bàn giao kho và so byte JSONL đều đạt. Các lỗi lịch sử được giữ cùng log. [Hồ sơ sơ bộ trước tag](../proof/phase-1/qa-headless.md) và [log sơ bộ](../proof/phase-1/unittest.txt) vẫn còn để đối chiếu.
