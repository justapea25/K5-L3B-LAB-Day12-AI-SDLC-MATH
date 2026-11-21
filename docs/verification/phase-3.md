# Ma trận truy vết Phase 3

2026-11-21 · tag `phase-3` · commit `e4daaf4` · Python 3.13.17 · Windows 11

Tiêu chí theo [kế hoạch Phase 3](../plan/phase-3.md). Kết quả bên dưới ghi phạm vi của từng ca kiểm.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P3-01 | `test_phase3.Contract.test_v12_freshness` | [Unittest](../proof/phase-3/unittest.txt) | Đạt. Manifest và các số chuẩn độ tươi khớp test. |
| AC-P3-02 | `test_kho_dem_va_sai_schema_ma_2`, `test_ngat_ghi_kho_rong` và smoke kho đếm | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Một phần. Đã kiểm dạng kho, kind lạ, ID trùng, fresh lớn hơn 100 và thiếu fresh. Chưa có ca fresh âm riêng. |
| AC-P3-03 | `test_id_tang_xuyen_ngay` và test giỏ LIFO từ Phase 1–2 | [Unittest](../proof/phase-3/unittest.txt) | Đạt trong các ca thứ tự giỏ và cấp ID qua ngày đã chạy. |
| AC-P3-04 | `test_hao_giu_va_quan` và `test_giu_tuoi_nhat_va_gia_theo_tuoi` | [Unittest](../proof/phase-3/unittest.txt) | Một phần. Đã đo hao trong giỏ và quán. Chưa kiểm đủ hàng mới, hàng giữ chỗ, món chín, kẹp 0 và pause. |
| AC-P3-05 | `test_nguong_30_o_buoc_dau`, `test_khong_giu_hang_uon` và smoke | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Một phần. Fresh 30 phát đúng một event ở tick 1. Chưa kiểm nhiều cá thể đồng thời và sức chứa. |
| AC-P3-06 | `test_ban_giao_file_va_quan_doc_lai`, `test_ngat_ghi_kho_rong` và ca tick limit giữ kho cũ | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Một phần. Đã kiểm dữ liệu và dung sai. Chưa kiểm thao tác thay thế nguyên tử. |
| AC-P3-07 | Smoke kho cá thể qua hai tiến trình và `test_ban_giao_file_va_quan_doc_lai` | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Đạt. ID, kind và fresh khớp trong dung sai 0,01. |
| AC-P3-08 | Chạy thêm `test_regression.DayHandoffRegression` trên mã game tại tag, cùng `test_id_tang_xuyen_ngay` | [Regression bổ sung](../proof/phase-3/regression-handoff.txt) · [Unittest](../proof/phase-3/unittest.txt) | Đạt trong các ca đã chạy. Kho quán nhận cả hàng ươn cùng tick cập bến, giữ ID và độ tươi khi chuyển pha và pause. Quán bắt đầu hao từ bước hoạt động kế tiếp. |
| AC-P3-09 | `test_giu_tuoi_nhat_va_gia_theo_tuoi` và ba ca giữ lại/ươn | [Unittest](../proof/phase-3/unittest.txt) | Một phần. Đã kiểm ưu tiên độ tươi và cấp lại. Chưa kiểm mọi trường hợp hòa ID và thứ tự nhiều đơn. |
| AC-P3-10 | `test_giu_tuoi_nhat_va_gia_theo_tuoi` và `test_quan_service` | [Unittest](../proof/phase-3/unittest.txt) | Một phần. Đã kiểm ID tiêu và giá chốt. Chưa kiểm riêng boa làm tròn theo giá suy giảm. |
| AC-P3-11 | Ca ươn tick đầu, giữ lại khi ươn, phục vụ tại biên giờ và đóng ca | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Một phần. Chưa có một replay ép toàn bộ bước xảy ra cùng tick. |
| AC-P3-12 | `test_kho_dem_va_sai_schema_ma_2`, `test_khong_giu_hang_uon` và fixture khách | [Unittest](../proof/phase-3/unittest.txt) | Một phần. Đã kiểm một số mâu thuẫn. Chưa rà hết ID trùng chéo giữa các nơi chứa. |
| AC-P3-13 | Test sự kiện ngất/cá sấu, kho quán và ca nấu theo ID | [Unittest](../proof/phase-3/unittest.txt) · [Smoke](../proof/phase-3/smoke.txt) | Một phần. Chưa kiểm riêng mọi trường schema Shop và sắp nhiều nguyên liệu ở `cook_started`. |
| AC-P3-14 | Chơi thử HUD độ tươi tại tag Phase 3 | — | Chưa kiểm chứng. |
| AC-P3-15 | Đối chiếu tag với lịch sử phần mở rộng | [Kế hoạch Phase 3](../plan/phase-3.md) · [Unittest Phase 4](../proof/phase-4/unittest.txt) | Chưa đạt tại tag Phase 3. Phần thực thi `burn` và `net` chỉ có từ tag Phase 4. |
| AC-P3-16 | Chạy unittest P1–P2, đối chiếu CHANGELOG và commit chuyển fixture `e0f00c2` | [Unittest](../proof/phase-3/unittest.txt) · [CHANGELOG](../../CHANGELOG.md) | Đạt trong bộ regression đã chạy. CHANGELOG ghi đổi schema và cách chuyển fixture. |
| AC-P3-17 | Kiểm tag và hồ sơ bàn giao | — | Một phần. Log khớp tag, hồ sơ này được bổ sung sau tag. |

## Kiểm lại phase trước

Unittest Phase 3 chạy các ca P1 và P2 còn hiệu lực. Các test giao kho chuyển sang fixture cá thể theo [clarify #19](../clarify.md). Xem [AC Phase 1](phase-1.md), [AC Phase 2](phase-2.md) và log tại AC-P3-16.

## Đánh giá ngắn

Cả 136 test đều qua. Smoke xác nhận cùng ID/kind, độ tươi file 99,991666… và snapshot 99,992, phát `spoiled` ở tick 1 và trả mã 2 với kho đếm. Các ca cần thêm tập trung vào ưu tiên nhiều đơn, thứ tự trong cùng tick và UI.
