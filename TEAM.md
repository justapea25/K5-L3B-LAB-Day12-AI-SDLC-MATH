# TEAM

**Tên nhóm:** math  **Số người:** 6  (khớp `team_size` trong `game.contract.json`)

| Thành viên | GitHub handle | Module chính | Vai quy trình | Người dự phòng cho |
|---|---|---|---|---|
| Đậu Hoàng Minh | justapea25 | `sim/gather` lát 1 (oxy, ngạt, Máu, giỏ) | Lead / Integrator | lát 2 |
| Lê Thế Anh (2A202603983) | LETHESHIYING | `sim/gather_harvest` lát 2 (hái, bắt cá) | Developer (Gather) | lát 1 |
| Nguyễn Việt Hoàng | viethoang127 | `sim/quan_customers` lát 3 (khách) | Developer | |
| Đặng Minh Thu (2A202604009) | minhthu27 | `sim/quan_service` lát 4 (bếp, phục vụ, tiền) | Developer, Scrum/Release | viethoang127 |
| Trần Xuân Lộc | Kaylez-TXL | `qa` (test hộp đen, verification) | QA lead | linkiewinkie |
| Nguyễn Xuân Khánh Linh | linkiewinkie | `docs` + harness AI, sau là `client/ui` | PO | |

**Vai quy trình:** PO (đầu mối hỏi giảng viên, giữ `docs/clarify.md`) · Integrator (giữ `docs/contracts/`, gắn tag) · QA lead · Scrum/Release. Có thể kiêm.

## Thỏa thuận làm việc nhóm (điền trong 15 phút kickoff, ≤ 10 dòng)

- Kênh liên lạc: nhóm chat chung của team; việc code trao đổi qua PR trên GitHub.
- Khi bất đồng về thiết kế: mỗi bên nói 2 phút, không xong thì Lead quyết và ghi lý do vào `docs/clarify.md`.
- Khi ai đó trễ hoặc vướng quá 10 phút: báo ngay trong nhóm chat, người dự phòng vào hỗ trợ.
- Giờ standup giữa phase: giữa mỗi phase, mỗi người 1 dòng trong `docs/standup.md`.
- Cách đọc code của nhau: mọi thay đổi qua PR, Lead review; lát cùng module (gather / quán) đọc chéo nhau.
- Cách làm việc với Git: mỗi người một nhánh ngắn `<handle>/<việc>`, mỗi người chỉ sửa file của lát mình; rebase `main` + chạy test trước khi mở PR; Lead gộp và gắn tag, khóa `main` 5 phút trước hạn tag.
