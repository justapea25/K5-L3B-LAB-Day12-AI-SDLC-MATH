# Kế hoạch Phase 2 (TICKET-02 — Một ngày ở chợ nổi)

- **Mục tiêu:** contract v1.1 với số chuẩn; cá bơi/sinh, Cá Sấu, 2 bếp/4 bàn, 6 món; chế độ `day` (kế hoạch D1–D5, Shop, pause); menu/HUD. Tag `phase-2` trước 1:55. Câu hỏi và quyết định: [clarify](../clarify.md) (#8 trở đi).
- **Nguyên tắc tránh conflict:** mỗi việc một file riêng; `gather.py` và khung chạy (`runner`, `headless`, `inputs`) do Lead giữ và đã nối sẵn lời gọi.

## Việc / người / phụ thuộc (Lead chia)

| Việc | Người | File | Phụ thuộc | AC |
|---|---|---|---|---|
| Contract v1.1 (số chuẩn, 6 nguyên liệu, 6 món, day_plan, shop, monsters), nối lời gọi gather theo thứ tự 4.5, sinh cá đầu ca/theo lịch, `faint` v1.1 | @justapea25 | `game.contract.json`, `chonoi/contract.py`, `gather.py`, `gather_fish.py` (phần sinh) | — (làm đầu tiên) | 01, 02, 04, 11 |
| Chế độ `day` + pause (đổi pha, `day_plan`, bàn giao kho, cấp nâng cấp), tích hợp, gắn tag | @justapea25 | `chonoi/day.py` (mới), `runner.py`, `headless.py`, `inputs.py` | contract v1.1, Shop | 13, 14, 17, 18, 19 |
| Cá bơi (đổi hướng theo seed, phản xạ mép), bắt cá 3 loài, hái kèo nèo | @LETHESHIYING | `gather_fish.py` (`swim`), `gather_harvest.py` | contract v1.1 | 03, 05 |
| Cá Sấu: patrol/chase/hit/recoil, bất tử, mất hàng LIFO, ngất do quái | @minhthu27 | `gather_monsters.py` | contract v1.1 | 06, 07, 08, 09 |
| Quán v1.1: 2 bếp/4 bàn, bếp nhận đơn cũ nhất, lọc món theo kế hoạch ngày, luật đóng ca | @viethoang127 | `quan.py`, `quan_customers.py`, `quan_service.py` | contract v1.1 | 10, 12 |
| Shop: mua oxygen/hp, `bought`/`buy_failed`, `shop_done`, tự đóng 600 tick; QA: cập nhật test P1 theo số chuẩn, smoke tích hợp (phút 20, 35), `verification/phase-2.md` | @Kaylez-TXL | `chonoi/shop.py` (mới), `tests/`, `docs/proof/phase-2/` | contract v1.1 | 15, 16, 22, 23, 24, 25 |
| PO: `clarify.md`, plan, AGENTS.md, skill; giao diện: menu, DayIntro/EveningIntro/DayResult/Summary, pause, HUD | @linkiewinkie | `chonoi/web/index.html`, `chonoi/live.py`, docs | snapshot v1.1 | 20, 21, 25 |

Mở rộng (nhóm 6 cần ≥ 2 trong cả buổi): để Phase 3–4 khi lõi đúng — Lead ưu tiên `burn` (quán) và `net` (bắt cá); PO chốt đầu Phase 3 ([clarify #16](../clarify.md)).

**Giao diện cần chốt sớm** (Lead chủ trì):
1. Vòng ngày dựng `GatherSim`/`QuanSim` mỗi Ngày, nhận `gather_end.inventory` trong bộ nhớ, truyền cấp đang áp dụng (`oxygen_max_s`, `hp_max`) vào khi dựng.
2. Trường snapshot UI đọc: `day`, `day_plan`, `upgrades`, `active_upgrades`, `phase` (`gather`/`quan`/`shop`), `state` (`playing`/`paused`/`finished`), `monsters[]`, `player.invuln_ticks`.
3. Hàm dùng chung giữa cá/Cá Sấu và `gather.py`: vị trí người chơi, giỏ (`_add_to_hold`), bỏ hàng LIFO (dùng chung cho ngất và hit).

## Tiêu chí chấp nhận (AC-P2-xx, nhóm tự đánh theo TICKET-02)

| AC | Nội dung | Nguồn |
|---|---|---|
| AC-P2-01 | `contract_version: "1.1"`, đủ khóa mới (bảng 4.1), số chuẩn mục 1 | 1, 4.1 |
| AC-P2-02 | 6 nguyên liệu, 6 món (công thức, nấu, giá) là dữ liệu; nút N5/N6 `keo_neo` | 1.1, 1.3 |
| AC-P2-03 | Cá bơi 1.5 m/s trong `x ∈ [4,96]` và dải độ sâu loài; đổi hướng theo seed ở bước bơi thứ 120, 240… trước khi di chuyển; phản xạ mép, chạm góc đảo cả hai | 1.1 |
| AC-P2-04 | Đầu ca 8 đàn ở 8 điểm khác nhau; mỗi `360·k` tick sau khi cá bơi sinh tối đa 1 đàn nếu < 12 và có điểm cách mọi đàn > 1 m; trọng số 40/30/30 chuẩn hóa lại; `fish_spawned`; cá mới tham gia từ bước sau | 1.1 |
| AC-P2-05 | Bắt cá theo vị trí cá trước khi bơi; yield linh 3, lóc 1, kèo 2; hồi 30 tick từ lần bắt thành công | 1.1, 4.5 |
| AC-P2-06 | Cá Sấu: patrol 1.0 m/s giữa 2 waypoint; chase 3.0 m/s khi người chơi d ≥ 10 và ≤ 10 m; về patrol khi > 16 m hoặc d < 10; chặn theo biên và dải `[10,30]`; M2 từ Ngày 3; gather độc lập dùng bố trí Ngày 1 | 1.2 |
| AC-P2-07 | Hit sau khi cả hai di chuyển: ≤ 1.5 m, d ≥ 10, hết bất tử → −1 Máu, bỏ `floor(n/2)` theo LIFO, bất tử 90 tick, `monster_hit`; tối đa 1 hit/bước, con gần nhất hòa theo id | 1.2, 4.4 |
| AC-P2-08 | Recoil 60 bước từ bước sau, lùi 2/60 m/bước theo hướng chốt lúc chạm (trùng tâm dùng +x), không gây hit; hết recoil về patrol | 1.2 |
| AC-P2-09 | Ngạt xuyên bất tử, không rơi hàng; Máu 0 → `faint` (`cause` choke/monster, `lost` là phần giỏ còn lại) rồi `gather_end fainted` ngay sau `choke`/`monster_hit`; trong `day` vẫn mở quán với kho rỗng | 1.1, 1.2, 4.5 |
| AC-P2-10 | Quán 2 bếp B1/B2, 4 bàn T1–T4; interact chọn gần nhất, bếp trước bàn, rồi id; khách ở tick 120 + 900·k nếu có bàn trống | 1.3 |
| AC-P2-11 | `day_plan` D1–D5 đúng bảng; `ingredients` = tổng công thức × số suất | 2, 4.1 |
| AC-P2-12 | Trong `day`, khách chọn đều theo seed trong món của kế hoạch đủ nguyên liệu khả dụng (vẫn gọi được khi đã bán đủ suất); quán độc lập dùng 6 món; thiếu món → `no_dish` | 2, 4.5 |
| AC-P2-13 | Đổi pha: `day_start → day_plan → phase_start(gather)`; sau `gather_end` phát `phase_start(quan)` cùng tick (kể cả ngất); sau `quan_end` phát `phase_start(shop)`; pha mới chạy từ bước sau; event có thêm `day` | 4.4, 4.5 |
| AC-P2-14 | Tiền, earned, uy tín, cấp giữ qua Ngày; oxy/Máu hồi đầy theo cấp có hiệu lực; giỏ làm mới, kho dư bỏ sau Shop | 2 |
| AC-P2-15 | Shop: mua cấp kế tiếp (đủ đúng giá vẫn mua), trừ `money`, giữ `earned`; `bought` / `buy_failed` (funds, max_level, unknown); cấp có hiệu lực từ Ngày kế (`active_upgrades` chỉ sao khi dựng Ngày mới) | 2, 4.5 |
| AC-P2-16 | Shop đóng bằng cạnh `shop_done` (`shop_end done`) hoặc sau 600 tick hoạt động (`shop_end time`); một `buy` xử lý trước `shop_done`; đóng Shop tăng `days_completed` | 2, 4.5 |
| AC-P2-17 | `--days` 1–5 (mặc định 1) chỉ với `day`; `end` có `days_completed`, đủ Ngày thì `reason: "days_complete"`; một Ngày không pause ≤ 22.200 tick | 4.1, 4.4 |
| AC-P2-18 | Pause: cạnh `pause` xét trước; vào pause chỉ tăng tick ngoài, phát `paused`, snapshot `state: "paused"`; timer/lịch đứng yên, bỏ qua hành động và `buy`; cạnh kế phát `resumed` và chạy gameplay ngay bước đó | 4.2 |
| AC-P2-19 | Inputs/scenario v1.1: `pause`, `shop_done`, `buy`; khối `day`; `gather.monsters[]`, `fish[].age_ticks`, `player.invuln_ticks`; cấm `quan.stock`/`quan.reputation` trong `day`; mâu thuẫn → mã 2 | 4.2, 4.3 |
| AC-P2-20 | Menu chính (Chơi, Thoát); DayIntro (tự chuyển sau 4 s hoặc khi nhấn phím), EveningIntro, DayResult, Shop, Summary; Esc/P pause làm mờ nền, có Tiếp tục và Về menu, dừng mọi timer | 2 |
| AC-P2-21 | HUD sáng: Máu, oxy (< 25% đổi màu), thời gian (≤ 30 s đổi màu), độ sâu, giỏ theo loại, cần lấy/đã lấy, hồi bắt, gợi ý hái/cập bến, "Thủy quái!" + viền tím, "Hết hơi!". HUD quán: đồng hồ ca, tiền ca, uy tín, món + kiên nhẫn từng bàn (< 25% đổi màu), tiến độ bếp, món đang cầm, kho khả dụng. Chữ không chân ≥ 18 px ở 1280×720, ≥ 30 FPS | 2 |
| AC-P2-22 | Smoke tích hợp `gather --inventory-out → quan --inventory` với số chuẩn, bằng chứng `docs/proof/phase-2/integration.*` | 5 |
| AC-P2-23 | Smoke `day --days 1` và nhiều Ngày (kiểm cấp nâng cấp áp từ Ngày kế); headless một Ngày ≤ 20 s | 4.1, DoD |
| AC-P2-24 | Regression P1 còn hiệu lực đạt với số chuẩn; test đổi vì luật mới có ghi lý do trong commit | DoD |
| AC-P2-25 | `docs/verification/phase-2.md` khớp commit tag; clarify, nhật ký AI, retro cập nhật | DoD |

## Lịch (55 phút)

| Phút | Việc |
|---|---|
| 0–5 | Lead gán người (xong); chốt 3 giao diện ở trên |
| 5–20 | Build 4 lát, Lead cập nhật `game.contract.json` v1.1 và contract |
| 20 | Smoke tích hợp (AC-P2-22), standup 2–3 phút, điều người sang lát trễ |
| 20–35 | Build tiếp, chốt luồng `day` |
| 35–45 | Smoke `day`, regression P1, verification, gắn tag |
| 45–50 | Retro (Scrum/Release) |
| 50–55 | Dự phòng, tag `phase-2` chậm nhất 1:55 |

## Rủi ro
- `day` phụ thuộc mọi lát → tích hợp sớm bằng fixture cố định, mỗi lát giữ test xanh trên `main`.
- Test ẩn kiểm lại Phase 1 với số chuẩn → test cũ đổi phải ghi lý do (đã đổi: số đàn cá đầu ca 6 → 8; P1 cần cá đứng yên thì dựng `random_fish: false`).
- Lead ôm nhiều việc (contract + `day` + khung + tích hợp): người xong sớm hỗ trợ `day`/pause ở phút 20.
- UI phụ thuộc snapshot v1.1 của `day`: làm HUD gather/quán trước bằng mode độc lập, nối `day` khi Lead có snapshot.
