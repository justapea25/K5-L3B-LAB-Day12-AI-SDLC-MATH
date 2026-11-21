# Day 12 — AI SDLC: Quán Ăn Chợ Nổi

> **Làm theo nhóm 4–6 người** · Dùng AI để xây game 2D qua **4 phase** trong **3 giờ**: Út Sen lặn bắt cá, hái rau trên mặt nước rồi tối mở quán phục vụ khách.
> **Yêu cầu từng phase mở đúng mốc giờ tại lab board:** **[Chợ Nổi Lab](https://claude.ai/artifact/E35v787wSx2wDgPTNhMVDg)** (cần đăng nhập claude.ai; có trợ giảng AI cho từng phase).

## Bắt buộc (chỉ có thế)

Cách làm việc kỹ thuật là **tự do** (push thẳng, nhánh + PR, pair, có hay không CI…). Cái bắt buộc:

1. **Một repo chung:** trưởng nhóm **fork** repo này, đặt tên `K5-L3B-LAB-Day12-AI-SDLC-<ten-nhom>`, thêm mọi thành viên làm collaborator (*Settings → Collaborators*, quyền Write) và để repo **public** (giảng viên xem được, không cần mời).
2. **Cả nhóm cùng commit** bằng tài khoản GitHub của mình, mỗi người **≥ 3 commit có nội dung** (làm cặp thì ghi `Co-authored-by:`).
3. **Điền [`TEAM.md`](TEAM.md):** danh sách thành viên + thỏa thuận làm việc nhóm; sửa `team_size` trong [`game.contract.json`](game.contract.json). Commit của người không có trong `TEAM.md` không được tính.
4. **Gắn tag** `phase-1` … `phase-4` đúng hạn; chạy được tại từng tag.
5. **Ghi chép tối thiểu:** `docs/verification/phase-n.md`, `docs/clarify.md`, `docs/ai-usage-log.md`, `docs/retro.md`, `docs/members/<handle>.md`.

## Chạy game (v1.0.0) — 3 lệnh từ clone sạch

**Yêu cầu:** Python ≥ 3.10 (chỉ thư viện chuẩn, không cần `pip install`), trình duyệt hiện đại. macOS hoặc Linux.

```bash
git clone https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH.git
cd K5-L3B-LAB-Day12-AI-SDLC-MATH
python3 -m chonoi.live --mode day        # mở địa chỉ in ra (mặc định http://127.0.0.1:8000/)
```

**Demo dễ chơi:** `python3 -m chonoi.live --mode day --demo` — sáng 2 phút, tối 2 phút, khách đến mỗi 8 s và kiên nhẫn 120 s, nấu nhanh gấp đôi, tầm bấm E rộng hơn, oxy 60 s, và tối nào Má Tư cũng đi chợ mua đủ nguyên liệu theo kế hoạch (chỉ cửa sổ chơi; headless giữ đúng luật). Kế hoạch món của Ngày luôn hiện ở HUD ("📋 Hôm nay Má Tư nấu").

Chơi vòng ngày (5 Ngày): Má Tư đọc món cần nấu → lặn hái → mở quán → Shop mua Bình oxy / Áo phao / Vợt. Chơi riêng một buổi: `--mode gather` hoặc `--mode quan`. Cổng khác: `--port 8765`.

### Điều khiển

| Phím | Buổi sáng (gather) | Buổi tối (quan) | Shop |
|---|---|---|---|
| WASD / mũi tên | Bơi ngang và lặn/nổi | Đi trong nhà bè | — |
| E | Cập bến hoặc hái nút trên mặt nước | Nấu ở bếp, bưng món, phục vụ ở bàn | — |
| Space | Bắt cá khi đang lặn | — | — |
| 1 / 2 / 3 | — | — | Mua Bình oxy / Áo phao / Vợt hút cá |
| Enter | — | — | Đóng Shop |
| P / Esc | Tạm dừng | Tạm dừng | Tạm dừng |
| H | Bật/tắt **tương phản cao** (hoặc mở với `?contrast=high`) | ← | ← |
| K | Bỏ qua buổi sáng (về bến) | Bỏ qua buổi tối (đóng ca) | Đóng Shop |
| N | Bật/tắt âm thanh (phụ đề SFX vẫn hiện) | ← | ← |
| R | Chơi lại | Chơi lại | Chơi lại |

**Cảnh báo (Phase 4):** 🐊 *Thủy quái!* + viền tím khi Cá Sấu trong 10 m ở vùng sâu · 🫧 *Oxy sắp hết!* (< 25%) / *Hết hơi!* (oxy 0) · 😠 *Khách sắp giận!* (kiên nhẫn < 25%, kèm số bàn). Giỏ có thanh **độ tươi** từng món, hàng ươn bị gạch chéo đỏ.

### Lệnh cho kiểm thử

| Việc | Lệnh |
|---|---|
| Test (regression P1–P4) | `PYTHONPATH=tests:. python3 -m unittest discover -s tests -v` |
| Headless một buổi | `python3 -m chonoi.headless --mode gather\|quan --seed 1 --ticks 600 --out out.jsonl` |
| Headless vòng ngày | `python3 -m chonoi.headless --mode day --days 5 --seed 1 --ticks 120000 --out day.jsonl` |
| Benchmark có render | `python3 -m chonoi.bench --seed 42 --duration 30 --out bench.json` |
| Soak headless | `python3 -m chonoi.soak --seed 7 --days 10 --out soak.json` |

Manifest: [`game.contract.json`](game.contract.json) (`contract_version: "1.3"`, `bench_cmd`, `soak_cmd`, `extensions`). Lịch sử theo phase: [`CHANGELOG.md`](CHANGELOG.md).

Tài liệu nhóm Math: [Kế hoạch](docs/plan/) · [Ma trận kiểm chứng](docs/verification/) · [Bằng chứng](docs/proof/) · [Câu hỏi cho PO](docs/clarify.md) · [Hướng dẫn cho agent](AGENTS.md)

### Cách tính điểm

`score = earned + 100 × floor(reputation)`: `earned` là tổng tiền thu (nghìn đồng, gồm boa), `reputation` là uy tín 0–5 (bắt đầu 3.0; khách hết kiên nhẫn −0.5, khách boa +0.2). Từ v1.2 giá món = floor(giá niêm yết × độ tươi trung bình / 100).

### Mở rộng đã làm

| Mục | Mã `extensions` | Phase | Test / bằng chứng |
|---|---|---|---|
| Cháy món: món chín để quá 20 s thì cháy, nguyên liệu mất, giữ lại cho đơn hoặc `unfulfillable` | `burn` | 3 (gộp sau tag `phase-3`, có từ `phase-4`) | [`tests/test_ext_burn_net.py`](tests/test_ext_burn_net.py) (`Burn`) |
| Vợt hút cá: mua ở Shop, cấp 1 bắt tối đa 2 đàn trong 4 m, cấp 2 tối đa 3 đàn trong 6 m | `net` | 3 (gộp sau tag `phase-3`, có từ `phase-4`) | [`tests/test_ext_burn_net.py`](tests/test_ext_burn_net.py) (`Net`), [`tests/test_extensions_manifest.py`](tests/test_extensions_manifest.py) |

### Sáng tạo của nhóm

| Ý tưởng | Phase | Tắt ở headless thế nào | Bằng chứng lõi vẫn đúng |
|---|---|---|---|
| HUD độ tươi: thanh màu dưới từng ô giỏ, gạch chéo hàng ươn, kho ghi độ tươi thấp nhất | 3 | Chỉ ở giao diện (`chonoi/web`), headless không đổi | Toàn bộ test headless xanh |
| Chế độ tương phản cao lưu lựa chọn giữa các lần mở (localStorage) | 4 | Chỉ ở giao diện | Toàn bộ test headless xanh |
| Chế độ demo "Má Tư đi chợ": `python3 -m chonoi.live --mode day --demo`, tối nào kho cũng có thêm đủ nguyên liệu theo kế hoạch để luôn có khách | sau 4 | Chỉ bật bằng cờ `--demo` của cửa sổ chơi; headless/`DaySession` mặc định tắt | Toàn bộ test headless xanh |
| Màn Kết quả Ngày (trong Shop) và Tổng kết sau Ngày cuối: khách phục vụ/bỏ đi, tiền, boa, uy tín, món bán chạy | sau 4 | Số liệu tính ở cửa sổ chơi, không thêm vào JSONL | Toàn bộ test headless xanh |
| Kỹ năng khi lặn: giữ F phóng to lưới (bắt nhiều đàn gần nhất), giữ G tăng tốc; mỗi kỹ năng trừ thêm oxy | sau 4 | `tuning.skills.enabled: false` trong contract; chỉ cửa sổ chơi bật, tắt bằng `--no-skills` ([clarify #23](docs/clarify.md)) | `tests/test_gather_skills.py`; toàn bộ test headless xanh |
| Tranh màu nước và sprite chibi (Út Sen, khách, bếp, Cá Sấu), cảnh quán nhà bè | sau 4 | Chỉ ở `chonoi/web` | Toàn bộ test headless xanh; nguồn ở [CREDITS](CREDITS.md) |
| Âm thanh SFX tổng hợp bằng WebAudio, có phụ đề (phím N tắt tiếng, phụ đề vẫn hiện), tiền bay lên, đom đóm | sau 4 | Chỉ ở `chonoi/web` | Toàn bộ test headless xanh; cần thêm bằng chứng chơi thử khi tắt tiếng |

"Sau 4" là gộp sau tag `phase-4`, nên không có trong Release v1.0.0 ([clarify #27](docs/clarify.md)).
| Âm thanh + **phụ đề SFX** (♪ cá quẫy, ting món chín, leng keng thu tiền, Cá Sấu đớp…), phím N tắt tiếng, phụ đề vẫn hiện | 4 | Chỉ giao diện (WebAudio) | Toàn bộ test headless xanh |
| Số tiền bay lên "+70k 💰" khi khách trả tiền, "+3 🐠" khi bắt cá; đom đóm trên sông buổi tối; thông báo sự kiện tiếng Việt | 4 | Chỉ giao diện | Toàn bộ test headless xanh |
| Tranh chợ nổi, nhà bè và nhân vật chibi (@Kaylez-TXL) + Cá Sấu chibi SVG tự vẽ, quay mặt theo hướng bơi/đuổi | 4 | Chỉ giao diện (`chonoi/web/art/`) | Toàn bộ test headless xanh |
| Phím K bỏ qua buổi (về bến / đóng ca / đóng Shop) bằng đúng luật, tiện demo | 4 | Chỉ cửa sổ chơi (`POST /skip`) | Toàn bộ test headless xanh |

## Tự do sáng tạo

Ngoài phần đề yêu cầu, nhóm được **thêm** nhân vật, loài cá/cây, sinh vật, món, bản đồ, cơ chế, câu chuyện, đồ họa, âm nhạc… với ba điều kiện: **không phá phần cố định** (tắt ở headless), ghi mục **"Sáng tạo của nhóm"** trong README của nhóm, và **làm lõi đúng trước**.

## Lịch 3 giờ

| Mốc | Phase | Hạn tag |
|---|---|---|
| 0:00 | Phase 1 (PRD-0) | `phase-1` trước 1:00 |
| 1:00 | Phase 2 | `phase-2` trước 1:55 |
| 1:55 | Phase 3 | `phase-3` trước 2:30 |
| 2:30 | Phase 4 | `phase-4` + Release `v1.0.0` trước 3:00 |

Hết giờ mỗi phase thì gắn tag rồi đi tiếp; chỗ chưa xong ghi trung thực trong bằng chứng.

## Đánh giá (100 điểm)

| Hạng mục | Điểm |
|---|---|
| Test tự động ẩn (headless, gồm kiểm tra lại phase trước) | 25 |
| Làm việc nhóm (một repo chung, chia việc, tích hợp, đổi yêu cầu) | 25 |
| Kiểm chứng & bằng chứng | 15 |
| Harness AI (AGENTS.md, skill, nhật ký dùng AI) | 10 |
| Đánh giá & retro | 10 |
| Chất lượng sản phẩm (đúng yêu cầu, mở rộng/sáng tạo) | 10 |
| Demo | 5 |

## Quy định

- Dùng AI thoải mái; **không sao chép repo của nhóm khác**; bằng chứng phải thật.
- Nhân vật, bối cảnh là bản gốc của lab; asset ngoài chỉ dùng CC0/CC-BY/MIT hoặc tự tạo, ghi nguồn trong `CREDITS.md`. Không commit API key, token, `.env`.
