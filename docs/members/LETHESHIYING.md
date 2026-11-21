# LETHESHIYING — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Gather lát 2: hái nút, bắt cá, hồi chiêu, `hold_full` ([e04b3fa](../../../../commit/e04b3fa)); 16 test hộp đen ([529642d](../../../../commit/529642d)); đổi payload theo PRD-0 ([1240566](../../../../commit/1240566)).
  - Sáng tạo: giữ F lưới lớn, giữ G tăng tốc, tắt mặc định ở headless ([f56e38a](../../../../commit/f56e38a), PR #20); phím theo `e.code` ([2ad2df5](../../../../commit/2ad2df5)).
- Tôi đã review (kèm link): code chủ yếu do AI viết nên tôi review theo chức năng: chạy thử game/headless, kiểm chức năng lát khác rồi phản hồi cho người viết (chưa có review inline trên PR).
- AI sai ở đâu và tôi phát hiện thế nào:
  - Hai test đầu sai (cá ở mặt nước; bấm `catch` liền không có cạnh lên). Test đỏ, tôi sửa test.
  - AI tự đặt tên trường sự kiện khác PRD-0 (`count` thay `amount`, `yield`). Sau khi merge `main`, test tích hợp của QA đỏ; tôi sửa theo PRD-0.
- Điều tôi học được: giả định chưa rõ phải hỏi PO; tên trường phải đối chiếu hợp đồng; tính năng thêm phải tắt mặc định và có test chứng minh luật lõi không đổi.
