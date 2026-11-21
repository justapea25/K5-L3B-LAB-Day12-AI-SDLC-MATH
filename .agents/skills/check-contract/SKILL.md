---
name: check-contract
description: So game.contract.json với số chuẩn Test Contract v1.3 (lõi TICKET-02 mục 1–2, 4.1; độ tươi TICKET-03; bench_cmd/soak_cmd TICKET-04) và in từng khóa thiếu/sai. Dùng sau khi sửa game.contract.json, trước khi mở PR đổi contract, và trước khi Lead gắn tag.
---

# check-contract — kiểm số chuẩn v1.3

```bash
python3 .agents/skills/check-contract/check_contract.py            # mặc định game.contract.json
python3 .agents/skills/check-contract/check_contract.py path.json  # file khác
```

- Mã 0 + `KHỚP`: đủ khóa lõi và đúng số chuẩn.
- Mã 1 + danh sách `- ...`: mỗi dòng là một khóa thiếu hoặc lệch, kèm giá trị chuẩn.

## Kiểm những gì

- `contract_version: "1.3"`; `bench_cmd`, `soak_cmd` ở gốc là chuỗi khác rỗng (v1.3).
- `tuning.freshness {initial: 100, gather_decay_per_s: 0.5, quan_decay_per_s: 0.25, spoiled_below: 30}` (v1.2).
- `extensions` là mảng chuỗi; có `burn` thì `tuning.quan.burn_s` là số dương, có `net` thì có `tuning.shop.upgrades.net`.
- Số chuẩn buổi sáng (bơi, oxy, giỏ, hái, bắt cá, `fish_*`), nút N1–N6, Cá Sấu (`gather.monsters`: loài `ca_sau`, M1, M2 từ Ngày 3, `invuln_ticks: 90`, `loss_ratio: 0.5`).
- Buổi tối: B1/B2, T1–T4, khách, boa, uy tín, `burn_s` có mặt (lõi `null`).
- 6 món (công thức, `cook_s`, giá), `day_plan` D1–D5 với `ingredients` tính lại từ công thức × số suất.
- Shop: `max_ticks: 600`, `upgrades.oxygen` (200 → 45 s, 400 → 60 s), `upgrades.hp` (250 → 4, 500 → 5).

## Không kiểm

- Giá trị chi tiết của khóa mở rộng (cấp `net`, `current`, `reservations`, `leaderboard`…): tùy nhóm chọn, kiểm bằng test riêng.
- Đơn vị `recoil_dist` (chỉ kiểm có mặt) và cách viết `fish_weights` (chỉ kiểm tỷ lệ 40/30/30).
- Dải hợp lệ của phase 1 (đã có trong `chonoi/contract.py`).

## Khi lệch

`game.contract.json` do Lead giữ: gửi danh sách lỗi cho Lead, đừng tự sửa. Script lệch với TICKET thì sửa script (file của PO) và ghi lý do trong commit.
