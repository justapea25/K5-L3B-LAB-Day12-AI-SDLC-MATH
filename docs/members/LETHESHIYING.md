# LETHESHIYING — phản tư cá nhân (≤ 200 từ)

- Tôi đã làm (kèm link commit):
  - Gather lát 2: hái nút, bắt cá, hồi chiêu, `hold_full` ([e04b3fa](../../../../commit/e04b3fa)); 16 test ([529642d](../../../../commit/529642d)); payload theo PRD-0 ([1240566](../../../../commit/1240566)).
  - Sáng tạo: giữ F lưới lớn, giữ G tăng tốc, tắt mặc định ở headless ([f56e38a](../../../../commit/f56e38a), PR #20); phím theo `e.code` ([2ad2df5](../../../../commit/2ad2df5)).
- Tôi đã review (kèm link): vì code do AI viết nên tôi review theo chức năng: chạy thử, phản hồi cho người viết.
  - Cá Sấu (`gather_monsters.py`): mất `floor(n×0.5)` món theo LIFO, bất tử 90 tick, hết Máu thì ngất và giỏ rỗng; không thấy lỗi.
  - Cá bơi/sinh (`gather_fish.py`): sinh mỗi 360 tick, tối đa 12 đàn, cá mới bắt được; không thấy lỗi.
- AI sai ở đâu và tôi phát hiện thế nào:
  - Hai test đầu sai (cá ở mặt nước; bấm `catch` liền không có cạnh lên); test đỏ nên tôi sửa.
  - AI đặt tên trường sự kiện khác PRD-0; test tích hợp của QA đỏ sau khi merge `main`, tôi sửa.
- Điều tôi học được: hỏi PO khi chưa rõ; tính năng thêm phải tắt mặc định và có test.
