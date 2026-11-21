# Credits

Liệt kê asset ngoài (nguồn, giấy phép CC0/CC-BY/MIT) và công cụ AI đã dùng.

## Khung và nội dung gốc

- Starter `chonoi/` và bộ test smoke: do giảng viên lab Day 12 cung cấp.
- Nhân vật, bối cảnh, nguyên liệu và món: bản gốc của lab (PRD-0).

## Asset

Không dùng asset tải từ nguồn ngoài (không ảnh, nhạc, font hay thư viện bên thứ ba). Mọi tài sản trong repo do nhóm tạo, một phần bằng công cụ AI. Tất cả phát hành chung theo [LICENSE](LICENSE) (MIT) của nhóm.

| Asset | Nguồn | Giấy phép | Dùng ở đâu |
|---|---|---|---|
| `chonoi/web/art/rach-sen.jpg`, `cho-noi.png`, `nha-be.jpg` | @Kaylez-TXL tạo bằng OpenAI ImageGen (commit `b63b38d`) | MIT (của nhóm) | Nền buổi sáng, chợ nổi, sàn nhà bè buổi tối |
| `chonoi/web/art/ut-sen-dong.png`, `ut-sen-lan.png`, `khach.png`, `bep-mon.png` | @Kaylez-TXL tạo bằng OpenAI ImageGen (commit `b63b38d`) | MIT (của nhóm) | Sprite Út Sen đứng/lặn, khách, bếp và món |
| `chonoi/web/art/ca-sau.svg` | @justapea25 vẽ SVG bằng mã, có Claude Code hỗ trợ | MIT (của nhóm) | Cá Sấu Năm Chèo |
| Âm thanh SFX | Tổng hợp tại chỗ bằng WebAudio (`AudioContext`) trong `chonoi/web/index.html`, không có file âm thanh | MIT (của nhóm) | Hiệu ứng âm thanh, kèm phụ đề |
| Hình khối HUD, cá, nút hái | Vẽ bằng canvas trong `chonoi/web/index.html`; `chonoi/bench.py` tự vẽ phần mềm | MIT (của nhóm) | Giao diện, benchmark |

Ảnh trong thư mục `assets/` ở máy cá nhân chưa được commit nên không thuộc bản phát hành. Ai muốn đưa vào repo thì ghi nguồn và giấy phép vào bảng trên trước.

## Công cụ AI

| Công cụ / model | Ai dùng | Dùng cho |
|---|---|---|
| OpenAI ImageGen, Codex | @Kaylez-TXL | Tranh màu nước chợ nổi Rạch Sen lúc bình minh, sàn nhà bè lên đèn và bộ sprite chibi gồm Út Sen, hai khách, ghe, bàn ăn, bếp đất, cá và hoa. Tài nguyên nằm trong `chonoi/web/art/`. |
| OpenAI ImageGen, Codex | @Kaylez-TXL | Sáu khách bổ sung (người già, trẻ em và người lớn), Út Sen đeo kính lặn, bốn tư thế bước và bốn nhịp bơi, bếp than, nồi đất, cá nướng, món nước và gỏi. |
| Claude Code (Claude Opus 5.5) | @justapea25 | Cá Sấu chibi `chonoi/web/art/ca-sau.svg` (SVG vẽ tay bằng mã, không dùng asset ngoài), âm thanh SFX tổng hợp bằng WebAudio |
| Claude Code (Claude Opus 5.5) | @justapea25, @linkiewinkie | Code lát 1, khung lát 2–4, contract v1.2–1.3, bench, soak; clarify, kế hoạch Phase 1–4, AGENTS.md, skill |
| Claude Code (Claude Sonnet 5.5) | @LETHESHIYING, @minhthu27 | Lát 2 (hái, bắt cá); lát 4 (quán) — theo nhật ký AI |
| Codex | @linkiewinkie | Bản nháp kế hoạch, TEAM, lệnh lưu bằng chứng |

Thành viên khác dùng công cụ AI nào thì nhắn @linkiewinkie để bổ sung. Chi tiết từng lần dùng ở [docs/ai-usage-log.md](docs/ai-usage-log.md).
