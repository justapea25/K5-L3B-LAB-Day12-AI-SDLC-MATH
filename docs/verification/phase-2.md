# Ma trận truy vết Phase 2

2026-11-21 · tag `phase-2` · commit `8ad6172` · Python 3.13.17 · Windows 11

Tiêu chí theo [kế hoạch Phase 2](../plan/phase-2.md). Kết quả bên dưới ghi phạm vi của từng ca kiểm.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P2-01 | `test_contract_v11.Contract.test_version_va_du_lieu_chuan` | [Unittest](../proof/phase-2/unittest.txt) | Đạt trong phạm vi khóa và số đã đối chiếu. |
| AC-P2-02 | `test_version_va_du_lieu_chuan` kiểm menu/nguyên liệu; đọc fixture chuẩn | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa rà hết giá, thời gian nấu và nút N5/N6. |
| AC-P2-03 | `test_phase2.FishSwim` kiểm tốc độ, vị trí và biên độ sâu | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa kiểm riêng đổi hướng ở tick 120/240 và phản xạ góc. |
| AC-P2-04 | `test_contract_v11.FishSpawn` kiểm số lượng, vị trí, seed và lịch sinh | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa kiểm đủ trọng số và điều kiện hết điểm sinh. |
| AC-P2-05 | `test_gather_harvest.Catch` kiểm yield và hồi chiêu | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa kiểm riêng thứ tự bắt trước khi bơi. |
| AC-P2-06 | `test_phase2.Monster` kiểm chase, hit và ca vùng nông | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa kiểm hết waypoint, ngưỡng rời chase và M2 ngày 3. |
| AC-P2-07 | `test_duoi_va_can_mat_nua_gio_lifo` | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Đã kiểm tick chạm, mất Máu, LIFO, bất tử. Chưa kiểm nhiều cá sấu chạm cùng bước. |
| AC-P2-08 | `test_duoi_va_can_mat_nua_gio_lifo` quan sát `recoil` sau hit | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa đo đủ 60 bước, hướng và độ lùi. |
| AC-P2-09 | Test ngất do cá sấu, test ngạt và `test_faint_v11_hp_0_lost_theo_lifo` | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa có ca day mở quán sau ngất và ngạt trong thời gian bất tử. |
| AC-P2-10 | `test_quan_customers.Spawn` và `test_quan_service.QuanService` | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Đã kiểm lượt khách và quy trình quán, chưa kiểm hết quy tắc chọn mục tiêu khi hòa. |
| AC-P2-11 | `test_day_plan_khop_de` kiểm kế hoạch D1–D5 | [Unittest](../proof/phase-2/unittest.txt) | Đạt trong ca đối chiếu dữ liệu. |
| AC-P2-12 | `test_quan_customers.Spawn.test_choice_is_seeded_and_only_feasible` và ca kho thiếu | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Đã kiểm chọn món đủ kho. Chưa ép tình huống đã bán đủ suất. |
| AC-P2-13 | `test_vong_ngay_va_shop` kiểm thứ tự và tick chuyển pha; smoke day | [Unittest](../proof/phase-2/unittest.txt) · [Vòng ngày](../proof/phase-2/day.txt) | Đạt trong vòng ngày chuẩn đã chạy. Ca ngất ở AC-P2-09 còn mở. |
| AC-P2-14 | `test_vong_ngay_va_shop` và replay nâng cấp xuyên ngày | [Unittest](../proof/phase-2/unittest.txt) · [Vòng ngày](../proof/phase-2/day.txt) | Một phần. Đã kiểm cấp oxy ngày kế và số tiền cuối replay, chưa kiểm đầy đủ hồi Máu, giỏ mới và bỏ kho dư. |
| AC-P2-15 | `test_vong_ngay_va_shop`, `test_buy_failed` và snapshot sau mua | [Unittest](../proof/phase-2/unittest.txt) · [Vòng ngày](../proof/phase-2/day.txt) | Một phần. Đã kiểm mua oxy, thiếu tiền, mã lạ và thời điểm áp dụng. Chưa kiểm mua đúng giá, cấp tối đa và giữ nguyên earned ngay lúc mua. |
| AC-P2-16 | `test_vong_ngay_va_shop` và smoke một ngày đủ 22.200 tick | [Unittest](../proof/phase-2/unittest.txt) · [Vòng ngày](../proof/phase-2/day.txt) | Một phần. Đã kiểm đóng tay và tự đóng. Chưa thử mua đồng thời với đóng Shop. |
| AC-P2-17 | `test_mot_ngay_khong_pause_22200_tick`, `test_day_cam_quan_stock_va_days_sai` và smoke day | [Unittest](../proof/phase-2/unittest.txt) · [Vòng ngày](../proof/phase-2/day.txt) | Đạt trong các ca ngày hợp lệ và giá trị ngoài giới hạn đã chạy. |
| AC-P2-18 | `test_pause_dung_dong_ho` xác nhận tick ngoài và timer gather | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa chạy pause khi đang mua Shop và lịch khách/cá ở mọi pha. |
| AC-P2-19 | `test_day_cam_quan_stock_va_days_sai`, test Cá Sấu và ca đầu vào v1.1 | [Unittest](../proof/phase-2/unittest.txt) | Một phần. Chưa kiểm đủ mọi trường và tình huống mâu thuẫn. |
| AC-P2-20 | Menu, màn đổi pha và pause trong trình duyệt ở tag Phase 2 | — | Chưa kiểm chứng. |
| AC-P2-21 | HUD sáng/tối, cảnh báo, cỡ chữ và FPS ở tag Phase 2 | — | Chưa kiểm chứng. |
| AC-P2-22 | Smoke hai tiến trình với kho đếm v1.1 | [Bàn giao kho](../proof/phase-2/integration.txt) | Đạt. Stock tick 0 khớp file gather xuất ra. |
| AC-P2-23 | Smoke một và ba ngày, kiểm nâng cấp và thời gian | [Vòng ngày](../proof/phase-2/day.txt) | Đạt. Một ngày 22.200 tick trong 1,421 giây, oxy có hiệu lực từ ngày 2. |
| AC-P2-24 | Chạy lại regression P1 qua unittest discover và so byte JSONL | [Unittest](../proof/phase-2/unittest.txt) · [Tính tất định](../proof/phase-2/determinism.txt) | Đạt trong bộ test đã chạy, gồm các ca tích hợp từng đỏ ở tag Phase 1. |
| AC-P2-25 | Kiểm tag và hồ sơ bàn giao | — | Một phần. Ma trận và log được bổ sung sau tag. |

## Kiểm lại phase trước

Các ca P1 còn hiệu lực được chạy lại trong `test_smoke_p1`, `test_gather_oxy`, `test_gather_harvest`, `test_integration`, `test_quan_customers`, `test_quan_service` và `test_live`. Xem [AC Phase 1](phase-1.md) và log của Phase 2 ở AC-P2-24. Test dùng luật v1.1 ở những chỗ hợp đồng đã đổi.

## Đánh giá ngắn

Cả 121 test đều qua. Smoke bàn giao kho, vòng ngày và so từng byte JSONL đều đạt. Cần thêm ca biên cho Cá Sấu và Shop, cùng một lượt chơi thử UI trên bản Phase 2.
