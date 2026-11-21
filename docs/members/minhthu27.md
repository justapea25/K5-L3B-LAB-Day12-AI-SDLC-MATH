# minhthu27 — phản tư cá nhân (≤ 200 từ)

> Đặng Minh Thu (2A202604009), lát 4 Quán + Scrum/Release.

- Tôi đã làm (kèm link commit):
  - Quán lát 4: `quan_service.py` (bếp nhận đơn cũ nhất, bưng, phục vụ, tiền, boa, uy tín, hết ca) ([137a724](../../../../commit/137a724), [b599639](../../../../commit/b599639)).
  - Test hộp đen lát 4, 8 test ([de5373b](../../../../commit/de5373b), [2389b97](../../../../commit/2389b97)).
  - Ghép lát 4 với `quan_customers` của lát 3 và contract v1.1 (2 bếp/4 bàn), đổi payload `served`/`paid` theo test QA ([9a0ff17](../../../../commit/9a0ff17)).
  - Scrum/Release: `docs/standup.md`, `docs/retro.md`, `CHANGELOG.md`.
- Tôi đã review (kèm link): đọc `quan_customers.py` và `customer.md` của lát 3 để ghép; đối chiếu test QA `tests/test_integration.py` với payload sự kiện. (bổ sung link PR khi có)
- AI sai ở đâu và tôi phát hiện thế nào: bản đầu AI tự thêm state `assigned`/`left` ngoài hợp đồng khách và đoán tên trường (`dish`, `patience_ticks`) trước khi có schema. Sau khi `customer.md` chốt theo PRD-0 (`dish_id`, `order_status`...), test đỏ nên phải viết lại một lượt. Bài học: chờ hợp đồng chốt rồi mới code.
- Điều tôi học được: tách file theo người và chốt tên hàm/sự kiện sớm giúp ghép lát 3 + 4 chỉ vá vài chỗ; test hộp đen của QA đọc theo PRD là nguồn chuẩn hơn tài liệu nhóm tự viết.
