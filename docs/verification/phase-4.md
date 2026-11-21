# Ma trận truy vết Phase 4

2026-11-21 · tag `phase-4` · commit `5e188e7` · Python 3.13.17 · Windows 11

Tiêu chí theo [kế hoạch Phase 4](../plan/phase-4.md). Kết quả bên dưới ghi phạm vi của từng ca kiểm.

| AC | Cách kiểm chứng | Bằng chứng | Kết quả |
|---|---|---|---|
| AC-P4-01 | `test_manifest_v13`, regression kho cá thể và lệnh kiểm contract v1.3 | [Unittest](../proof/phase-4/unittest.txt) · [Đối chiếu bản phát hành](../proof/phase-4/release.txt) | Đạt trong các kiểm tra manifest và bộ regression đã chạy. |
| AC-P4-02 | Chạy benchmark seed 42 trong 30 giây và đối chiếu cảnh sáng, cấu hình 1280×720, warm-up 3 giây trong mã tại tag | [Mã cấu hình tại tag](../proof/phase-4/release.txt) · [Log benchmark](../proof/phase-4/determinism.txt) | Đạt trong lần chạy đã ghi. |
| AC-P4-03 | `test_bench_json` và kiểm 5 trường của artifact | [Unittest](../proof/phase-4/unittest.txt) · [Benchmark gốc](../proof/phase-4/bench.json) · [Tính tất định](../proof/phase-4/determinism.txt) | Đạt trong các kiểm tra schema và công thức đã chạy. |
| AC-P4-04 | Đối chiếu ba mốc benchmark với kết quả chạy lại trên tag | [Benchmark gốc](../proof/phase-4/bench.json) · [Tính tất định](../proof/phase-4/determinism.txt) | Đạt mốc tham chiếu. Trung bình 896,90 FPS, 1% low 338,85 FPS, tải 98 ms. Đây là FPS framebuffer phần mềm. |
| AC-P4-05 | Chạy soak seed 7, 10 ngày và `test_soak_json_va_tat_dinh` | [Unittest](../proof/phase-4/unittest.txt) · [Soak gốc](../proof/phase-4/soak.json) · [Tính tất định](../proof/phase-4/determinism.txt) | Một phần. Đã kiểm hoàn thành 10 ngày. Chưa xác nhận hết trạng thái phải duy trì bằng log từng pha. |
| AC-P4-06 | So schema và hai lần chạy soak sau khi bỏ `duration_s` | [Unittest](../proof/phase-4/unittest.txt) · [Soak gốc](../proof/phase-4/soak.json) · [Tính tất định](../proof/phase-4/determinism.txt) | Đạt. 10/10 ngày, 0 crash, các trường còn lại giống nhau. |
| AC-P4-07 | Chạy live với cảnh gather oxy thấp gần Cá Sấu và cảnh quán khách sắp hết kiên nhẫn | [Ảnh gather](../proof/phase-4/canh-bao-gather.png) · [Ảnh quán](../proof/phase-4/canh-bao-quan.png) · [Fixture và log](../proof/phase-4/canh-bao.txt) | Đạt. Thấy viền tím, cảnh báo Thủy quái, oxy thấp và khách sắp giận tại bàn T1. |
| AC-P4-08 | Bật tương phản cao bằng H trong hai cảnh và chụp lại ba cảnh báo | [Ảnh gather](../proof/phase-4/canh-bao-gather-tuong-phan-cao.png) · [Ảnh quán](../proof/phase-4/canh-bao-quan-tuong-phan-cao.png) · [Log](../proof/phase-4/canh-bao.txt) | Đạt. Cả ba cảnh báo hiển thị chữ vàng trên nền đen. |
| AC-P4-09 | Clone tag công khai từ GitHub trên Ubuntu WSL, chạy live và kiểm HTTP `/` cùng `/state`. Chạy thêm một bản clone cục bộ trên Windows. | [Clone GitHub trên Linux](../proof/phase-4/clean-clone-linux.txt) · [Clone cục bộ trên Windows](../proof/phase-4/clean-clone.txt) | Đạt trên Linux. Sau 3 lệnh, giao diện và snapshot cùng trả HTTP 200. README tại tag có yêu cầu môi trường, điều khiển và các lệnh kiểm thử. |
| AC-P4-10 | Đọc release notes, tải và kiểm ZIP phát hành, chạy headless từ thư mục giải nén | [Log GitHub Release và smoke ZIP](../proof/phase-4/release-github.txt) | Đạt. Release có ghi điểm mới, cách chạy và giới hạn. ZIP chạy hết một ngày, mã thoát 0. |
| AC-P4-11 | Rà CHANGELOG, CREDITS và LICENSE tại commit bàn giao | [Đối chiếu bản phát hành](../proof/phase-4/release.txt) | Một phần. Rà hiện diện và phạm vi tài liệu, chưa kiểm nguồn của toàn bộ asset. |
| AC-P4-12 | Chạy unittest discovery với test P1–P3, smoke và ca hồi quy kho cá thể khi pause | [Unittest](../proof/phase-4/unittest.txt) · [Smoke](../proof/phase-4/smoke.txt) · [Tính tất định](../proof/phase-4/determinism.txt) · [Regression bổ sung](../proof/phase-4/regression-handoff.txt) | Đạt trong bộ regression đã chạy. |
| AC-P4-13 | Đối chiếu commit đích, giờ tạo hai tag và thời gian xuất bản Release | [Đối chiếu bản phát hành](../proof/phase-4/release.txt) · [Log GitHub](../proof/phase-4/release-github.txt) | Hai tag cùng trỏ `5e188e7`. GitHub ghi xuất bản 11:38:41, hai annotated tag hiện có ghi 11:42:58 (UTC+7). Chưa đối chiếu mốc bắt đầu buổi lab. |
| AC-P4-14 | Kiểm ma trận, bằng chứng, clarify và AI log tại tag | [Đối chiếu bản phát hành](../proof/phase-4/release.txt) | Một phần. Bằng chứng chạy lại khớp commit; ma trận và nhật ký QA cập nhật sau tag. |
| AC-P4-15 | Kiểm retro và file thành viên tại tag | [Đối chiếu bản phát hành](../proof/phase-4/release.txt) | Chưa đạt tại tag. Retro còn mẫu trống và chưa đủ hồ sơ cá nhân. |
| AC-P4-16 | Đối chiếu phạm vi v1.0.0 và phần phụ đề SFX gộp sau tag | [Đối chiếu bản phát hành](../proof/phase-4/release.txt) | Ngoài phạm vi bản tag. Chưa kiểm chứng phụ đề SFX sau tag. |

## Kiểm lại phase trước

Unittest Phase 4 chạy lại các bộ P1–P3, gồm `test_integration`, `test_phase2`, `test_contract_v11` và `test_phase3`. Xem [AC Phase 1](phase-1.md), [AC Phase 2](phase-2.md), [AC Phase 3](phase-3.md) và log tại AC-P4-12.

## Đánh giá ngắn

Cả 145 test trên tag đều qua. Benchmark chạy đủ 30 giây trên bộ vẽ phần mềm. Soak hoàn thành 10/10 ngày với 0 crash. Cả ba cảnh báo xuất hiện ở chế độ mặc định và tương phản cao. ZIP phát hành chạy headless hết một ngày.
