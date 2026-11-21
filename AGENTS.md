# AGENTS.md — hướng dẫn chung cho mọi agent AI của nhóm

> Cập nhật file này qua các phase (lịch sử git phải cho thấy điều đó). Ngắn gọn, có lệnh chạy thật. Người giữ: @linkiewinkie (PO); ai cần thêm thì nhắn.

## Lệnh
- Test (regression P1–P4): `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v`
- Headless một buổi: `python3 -m chonoi.headless --mode gather --seed 1 --ticks 600 --out out.jsonl` (đổi `gather` thành `quan` để thử quán).
- Bàn giao kho qua file (v1.2): `--inventory-out kho.json` ở `gather`, rồi `--inventory kho.json` ở `quan`. Kho là `{"items":[{id,kind,fresh}]}`; kho đếm cũ trả mã 2.
- Headless vòng ngày: `python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 22200 --out day.jsonl` (`--days` 1–5; một Ngày không pause ≤ 22.200 tick, phải chạy ≤ 20 s).
- Benchmark (v1.3): `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json`. Soak: `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json`.
- Chơi thử: `python3 -m chonoi.live --mode day` (hoặc `gather`, `quan`; thêm `--demo` để dễ chơi, `--no-skills` để tắt kỹ năng F/G). Mở địa chỉ in ra. Phím WASD, E, Space, 1/2/3 + Enter ở Shop, P/Esc tạm dừng, H tương phản cao, N tắt tiếng, R chơi lại.
- Kiểm `game.contract.json` theo số chuẩn v1.3: skill `check-contract`.
- **Windows:** `python3` có thể chỉ là lối tắt Microsoft Store (lỗi 9009, test con đỏ hàng loạt). Kiểm `python3 --version`; nếu không chạy, chép `python.exe` thành `python3.exe` trong thư mục cài Python (đứng trước `WindowsApps` trong PATH) hoặc tắt App execution aliases. Trên PowerShell: `$env:PYTHONPATH = 'tests;.'; $env:PYTHONUTF8 = '1'` rồi chạy unittest (thiếu `PYTHONUTF8` sẽ in traceback `UnicodeDecodeError` dù test vẫn đạt).

## Đọc trước khi sửa
- Yêu cầu phase: PRD/ticket trên lab board. PO tóm tắt trong kế hoạch từng phase, có danh sách AC: [Phase 1](docs/plan/phase-1.md) (AC-P1-xx, v1.0), [Phase 2](docs/plan/phase-2.md) (AC-P2-xx, v1.1), [Phase 3](docs/plan/phase-3.md) (AC-P3-xx, v1.2), [Phase 4](docs/plan/phase-4.md) (AC-P4-xx, v1.3). Phase sau **không** được làm hỏng AC phase trước (test ẩn kiểm lại).
- Quyết định cho chỗ PRD mơ hồ: [docs/clarify.md](docs/clarify.md). **Tên event, tên trường và `data` lấy nguyên văn PRD-0 mục D/E, TICKET-02 mục 4.4, TICKET-03 (JSONL) và TICKET-04.**
- Số liệu: số chuẩn TICKET-02 mục 1–2, cộng `tuning.freshness` của TICKET-03. Hiện tại `contract_version: "1.3"`: gameplay, kho, JSONL theo v1.2, thêm `bench_cmd`/`soak_cmd`.
- Độ tươi tính bằng số nguyên (240 đơn vị/điểm), so ngưỡng 30 trước khi làm tròn; đừng đổi sang số thực ([clarify #18](docs/clarify.md)).
- Hợp đồng tích hợp: [docs/contracts/](docs/contracts/README.md) (kho, sự kiện, schema khách).

## Cấu trúc & ai giữ file

| File | Nội dung | Người giữ |
|---|---|---|
| `chonoi/sim/gather.py` | Lát 1: oxy, ngạt, Máu, ngất, dive/surface, giỏ LIFO, helper `_add_to_hold`, cấp id và hao tươi (v1.2) | @justapea25 |
| `chonoi/sim/gather_harvest.py` | Lát 2: `try_gather` (hái), `try_catch` (bắt cá), mọc lại, hồi chiêu, `hold_full`; mở rộng `net` | @LETHESHIYING |
| `chonoi/sim/gather_fish.py` | Cá bơi (`swim`) / sinh cá | @LETHESHIYING / @justapea25 |
| `chonoi/sim/gather_monsters.py` | Cá Sấu: patrol, chase, hit, recoil, bỏ hàng LIFO | @minhthu27 |
| `chonoi/sim/gather_skills.py` | Sáng tạo: kỹ năng F/G, tắt ở headless (`skills.enabled: false`) | @LETHESHIYING |
| `chonoi/day.py`, `chonoi/bench.py`, `chonoi/soak.py` | Vòng ngày, bàn giao kho; benchmark; soak (v1.3) | @justapea25 |
| `chonoi/shop.py` | Shop: mua nâng cấp, `shop_done`, tự đóng 600 tick | @Kaylez-TXL |
| `chonoi/sim/quan_customers.py`, `chonoi/scenario.py` | Lát 3: `spawn_customers`, `tick_customers` (khách đến, chọn món, giữ chỗ, kiên nhẫn, khách rời) | @viethoang126 |
| `chonoi/sim/quan.py`, `chonoi/sim/quan_service.py` | Lát 4: interact, bếp, bưng, phục vụ, tiền, boa, uy tín, `quan_end` | @minhthu27 |
| `tests/test_integration.py`, `docs/verification/`, `docs/proof/` | Test hộp đen theo AC, bằng chứng | @Kaylez-TXL |
| `tests/test_phase2.py`, `test_phase3.py`, `test_phase4.py`, `test_ext_burn_net.py`, `test_extensions_manifest.py` | Test theo phase và mở rộng | @justapea25 |
| `game.contract.json`, `docs/contracts/` | Contract, số liệu | @justapea25 |
| `docs/clarify.md`, `docs/plan/`, `AGENTS.md`, `.agents/skills/`, `README.md`, `CREDITS.md` | PO, harness AI, docs | @linkiewinkie |
| `docs/standup.md`, `docs/retro.md`, `CHANGELOG.md` | Scrum/Release | @minhthu27 |
| `chonoi/web/index.html` (từ Phase 2) | Menu, màn chuyển pha, pause, HUD, cảnh báo, tương phản cao, âm thanh/phụ đề | @linkiewinkie (từ Phase 3 nhiều người cùng sửa: báo trong nhóm chat trước khi sửa) |
| `chonoi/web/art/` | Tranh và sprite (nguồn ghi trong `CREDITS.md`) | @Kaylez-TXL |

- **Phase 2:** việc mới (cá bơi/sinh, Cá Sấu, vòng ngày, Shop, pause) đặt trong **file mới** `chonoi/sim/<việc>.py`; file cũ chỉ thêm vài dòng nối. Lead gán người và ghi vào [plan Phase 2](docs/plan/phase-2.md); khi có tên, PO cập nhật bảng này.
- Khung do giảng viên cấp: `chonoi/{headless,inputs,contract,rng,ids,jsonl,inventory,runner,live}.py`. **Không sửa**; bắt buộc phải sửa thì báo cả nhóm, một người làm, ghi lý do. Phase 2 bắt buộc sửa khung cho `--mode day`, pause, `buy`/`shop_done`, scenario v1.1: chỉ **một người** (Lead gán) sửa các file này.
- Pause: khi `state` là `paused`, mọi timer gameplay, lịch khách/cá và Shop đứng yên; chỉ tick ngoài tăng.
- Mỗi người một file test riêng (`tests/test_<lát>.py`); không sửa `tests/test_smoke_p1.py`, `tests/helpers.py`. Cần dữ liệu thì tự dựng scenario trong test. Ngoại lệ duy nhất đến nay: Phase 3 Lead sửa hai file này để chuyển fixture sang kho cá thể (`migrate_scenario`, [clarify #19](docs/clarify.md)). Test mới dựng kho bằng mảng cá thể, đừng dựa vào bộ chuyển tự động.
- **Số liệu chỉ đọc từ `game.contract.json` / dữ liệu**, không hard-code trong luật.
- Mọi số ngẫu nhiên đi qua `Streams` (`chonoi/rng.py`); không dùng `random` toàn cục, không dùng đồng hồ hệ thống.
- Sắp danh sách thực thể bằng `ids.sort_by_id`; cấp id bằng `IdAllocator`.

## Quy tắc nhóm (Git)
- Nhánh ngắn `<handle>/<việc>`; commit nhỏ, thường xuyên; làm cặp thì ghi `Co-authored-by:`.
- Trước khi push: `git fetch && git rebase origin/main`, rồi chạy skill `run-tests`.
- Mở PR vào `main` trước phút 50; Lead (@justapea25) review, gộp, gắn tag. Test đỏ thì không gộp.
- Thứ tự gộp: helper giỏ (lát 1) trước lát 2; schema khách (lát 3) trước lát 4. Phase 2: `game.contract.json` v1.1 và sửa khung `day` lên trước, rồi các lát dùng chúng. Phase 3: contract v1.2 + adapter kho → test và chuyển fixture → CHANGELOG. Đổi contract lần sau cũng theo thứ tự: contract/adapter trước, rồi các lát.
- Test cũ phải đổi vì luật/số chuẩn mới: ghi lý do trong commit (vd. "P1 dùng cá đứng yên F1–F6, v1.1 cá bơi → dựng scenario `random_fish: false`").
- Conflict ở file người khác giữ → giữ bản trên `main`, nhắn chủ file. Vướng quá 10 phút → báo nhóm, người dự phòng vào.
- File dùng chung (`TEAM.md`, `docs/ai-usage-log.md`): mỗi người chỉ sửa dòng/mục của mình, `git pull --rebase` ngay trước khi sửa.

## Nên tránh
- Không sửa `docs/contracts/`, `game.contract.json` (khóa contract) hoặc schema kho khi chưa báo cả nhóm (đổi hợp đồng ảnh hưởng mọi module).
- Không sửa file của người khác (bảng trên); cần đổi thì nhắn chủ file.
- Không làm hỏng nhánh chính: trước khi đẩy, chạy test.
- Không bịa yêu cầu: chỗ mơ hồ thì ghi `docs/clarify.md` và hỏi PO.
- Không sửa test cho xanh khi luật sai; phải sửa luật hoặc ghi lý do đổi test trong commit.

## Quy tắc làm việc với agent
- Mỗi agent một việc rõ ràng (một lát). Cho agent đọc PRD/ticket đúng phase, `docs/clarify.md` và hợp đồng trước.
- Agent chỉ sửa file của người đang dùng nó (bảng trên).
- Agent làm xong phải chạy test và ghi kết quả vào mô tả commit/PR; người đọc lại thay đổi trước khi đẩy.
- Ghi mỗi lần dùng AI vào mục của mình trong `docs/ai-usage-log.md` (công cụ, việc, AI sai ở đâu).
- Sáng tạo thêm được khuyến khích nhưng phải tắt ở headless (xem README, mục "Tự do sáng tạo").

## Skills / hooks của nhóm

| Skill | Khi nào dùng |
|---|---|
| [`run-tests`](.agents/skills/run-tests/SKILL.md) | Trước khi push/mở PR, sau khi gộp, trước khi gắn tag: unittest + smoke hai tiến trình + kiểm tra cùng seed giống từng byte |
| [`verify-phase`](.agents/skills/verify-phase/SKILL.md) | Phút 45–55 mỗi phase: điền `docs/verification/phase-n.md` theo AC-P{n}-xx với bằng chứng thật |
| [`check-contract`](.agents/skills/check-contract/SKILL.md) | Sau khi sửa `game.contract.json`, trước khi gộp: so với số chuẩn v1.3 (lõi v1.1, `freshness`, `bench_cmd`/`soak_cmd`, khóa của mở rộng đã khai), liệt kê khóa thiếu/sai |
