# Retro nhóm

## Phase 2 (nhanh)
- Điều tốt: mỗi lát một file riêng (`gather_harvest`, `quan_customers`, `quan_service`) nên ghép gần như không conflict; Lead chốt contract v1.1 sớm nên các lát có số chuẩn để dùng; QA đọc PRD nên bắt được lệch tên trường sớm.
- Điều tệ: hợp đồng nhóm tự viết (`events.md`, `customer.md`) lệch PRD-0 ở tên trường (`dish` vs `dish_id`, `customer_id` vs `order_id`) nên lát 4 phải viết lại một lượt; có test lát 3 còn giả định 1 bàn khi contract v1.1 có 4 bàn; có lần đẩy thẳng `main` thay vì qua PR nên `main` đỏ vài test của người khác.
- 1 hành động cho Phase 3: mọi tên event/trường lấy nguyên văn PRD/ticket (PO dán vào `clarify.md`) trước khi code; chạy `run-tests` trên `main` mới nhất trước khi mở PR và ghi test đỏ của người khác vào standup thay vì sửa hộ.

## Phase 4 (cuối)
- Rà lại hành động Phase 2: làm được một phần. Từ Phase 3 payload theo PRD (QA kiểm bằng `test_integration.py`), nhưng việc chạy test trước khi mở PR còn làm tay, và trên Windows còn vướng `python3` (xem dưới).
- Điều tốt / điều tệ: tốt: đủ tag `phase-1`…`phase-4` và `v1.0.0`, contract tăng v1.1 → v1.3 có CHANGELOG, giao diện quán có chỉ dẫn từng bước và báo vì sao chưa có khách. Tệ: người chơi dễ tưởng quán lỗi khi bắt sai loại cá so với kế hoạch Ngày (khách chỉ chọn món trong kế hoạch và cần đủ nguyên liệu); `headless_cmd` gọi `python3` nên test đỏ hàng loạt trên Windows nếu chưa có `python3`.
- Số liệu: số commit không-merge theo người trong lịch sử repo: justapea25 (Đậu Hoàng Minh) 59, NguyenXuanKhanhLinh (linkiewinkie) 24, LETHESHIYING 17, minhthu27 14, Kaylez-TXL 8 (6 + 2 dưới tên `XuanLoc`), viethoang126 6 (hiện dưới tên `viethoang127`, cần kiểm email/handle git). Cách đọc code của nhau: qua PR và ghép lát cạnh nhau (lát 3 ↔ lát 4 đọc code nhau khi ghép; QA đối chiếu payload). Token theo người: xem cột token trong `docs/ai-usage-log.md` (nhiều bạn ghi "chưa đo").
- Một lần AI sai và cách nhóm phát hiện: AI viết lát 4 với state `assigned`/`left` và tên trường tự đoán; phát hiện khi `customer.md` chốt theo PRD-0 và test QA đọc payload `served`/`paid` khác, nên viết lại theo `dish_id`/`order_id`/`order_status`.
- Nếu làm lại, đổi gì: dán PRD vào repo ngay phút đầu để mọi lát dùng cùng tên trường; thêm `python3` shim cho Windows vào skill `run-tests`; mỗi lát có người đọc chéo bắt buộc trước khi gộp; không đẩy thẳng `main`.
