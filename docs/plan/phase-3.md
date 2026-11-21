# Kế hoạch Phase 3 (TICKET-03 — Change Request "Mùa Nước Nổi")

- **Mục tiêu:** contract v1.2: kho cá thể `{id, kind, fresh}`, độ tươi và hàng ươn, giữ chỗ theo id, giá theo độ tươi; bàn giao kho qua file và trong `day`; HUD độ tươi. Tag `phase-3` trước 2:30. Câu hỏi và quyết định: [clarify](../clarify.md) (#18 trở đi).
- **Ghi chú:** bản này PO viết lại sau khi tích hợp, đối chiếu `git log phase-2..phase-4`. Ở Phase 3 Lead làm gần hết phần lõi trong một lượt để `main` không bị vỡ giữa hai schema kho.

## Phân tích tác động (đổi schema kho)

| Module | File cần đổi | Test bị ảnh hưởng | Người phụ trách |
|---|---|---|---|
| Adapter kho, contract | `game.contract.json` (`1.2`, `tuning.freshness`), `chonoi/inventory.py`, `chonoi/contract.py`, `chonoi/scenario.py` | Thêm `test_phase3.Contract`; mọi test dựng `hold`/`stock` kiểu đếm | @justapea25 |
| Lặn | `chonoi/sim/gather.py` (cấp id, hao tươi, `spoiled`, `lost` là cá thể), `gather_monsters.py` (bỏ hàng LIFO) | `test_gather_*`, `test_phase2` (kiểm `lost`) | @justapea25 |
| Quán | `chonoi/sim/quan.py`, `quan_customers.py` (giữ theo id, giữ lại khi vừa ươn), `quan_service.py` (tiêu id, chốt giá) | `test_quan_*`: giá 60 → 59 vì hàng đã hao một tick | @justapea25 |
| `day`, Shop | `chonoi/day.py` (bàn giao cùng tick, id tăng xuyên Ngày), `chonoi/shop.py` (snapshot `stock` cá thể) | Thêm `test_phase3.Day` | @justapea25 |
| HUD | `chonoi/web/index.html` | Chơi thử | @justapea25 |
| Fixture | `tests/helpers.py` (`migrate_scenario`, `kinds`, `counts`, `same_items`), `tests/test_smoke_p1.py` (so kho theo cá thể) | Mọi test cũ tự chuyển schema qua `write_json` | @justapea25 (ngoại lệ: hai file "không sửa", xem [clarify #19](../clarify.md)) |
| QA, docs | `docs/verification/phase-3.md`, `docs/proof/phase-3/`, `CHANGELOG.md`, `docs/clarify.md` | — | @Kaylez-TXL, @minhthu27, @linkiewinkie |

**Quyết định đổi schema:** đổi thẳng sang v1.2, không chạy song song hai schema trong nội bộ. Bên đọc thấy file kho đếm thì trả mã 2. Fixture cũ được chuyển tự động trong `tests/helpers.py`, nên test P1–P2 giữ nguyên ý nghĩa.

**Thứ tự tích hợp:** (1) contract v1.2 cùng adapter kho (`55adcbf`) → (2) test Phase 3 và chuyển fixture (`e0f00c2`) → (3) CHANGELOG breaking change (`eeb6660`) → (4) manifest `extensions` (`ca3366c`, `bd2c366`). Tag `phase-3` trỏ commit `e4daaf4`. Phần thực thi `burn`/`net` (`7322434`) được gộp **sau** tag `phase-3`, nên chỉ có từ `phase-4`.

## Tiêu chí chấp nhận (AC-P3-xx, nhóm tự đánh theo TICKET-03)

| AC | Nội dung | Nguồn | Kiểm bằng |
|---|---|---|---|
| AC-P3-01 | `contract_version: "1.2"`, `tuning.freshness {initial: 100, gather_decay_per_s: 0.5, quan_decay_per_s: 0.25, spoiled_below: 30}` | Contract v1.2 | `test_phase3.Contract.test_v12_freshness` |
| AC-P3-02 | File kho đúng một khóa gốc `items`, là mảng `{id, kind, fresh}`; kho rỗng `{"items":[]}`. Kho đếm, sai schema, kind lạ, id trùng hoặc `fresh` ngoài [0,100] → mã 2 | 1 | `test_kho_dem_va_sai_schema_ma_2` |
| AC-P3-03 | Cấp id I1, I2… theo thứ tự vào giỏ, tăng liên tục xuyên pha và Ngày; Ngày kế cấp id mới cho mẫu `gather.hold`; LIFO theo thứ tự vào giỏ | 1, Scenario | `test_phase3.Day.test_id_tang_xuyen_ngay` |
| AC-P3-04 | Hàng mới `fresh = 100`, bắt đầu hao từ bước sau; giỏ −0.5/s, kho quán −0.25/s (kể cả hàng đang giữ); kẹp ở 0; pause dừng hao; món chín không hao | Bảng độ tươi | `test_hao_giu_va_quan` |
| AC-P3-05 | Ươn khi `fresh < 30`: vẫn chiếm ô, không dùng nấu; `spoiled {item_id, kind, location}` đúng một lần khi đi từ ≥ 30 xuống < 30, nhiều cá thể thì theo id; so ngưỡng trước khi làm tròn. Fixture `fresh: 30` phát `spoiled` ở tick 1 | Bảng độ tươi, JSONL | `test_nguong_30_o_buoc_dau` |
| AC-P3-06 | `gather --inventory-out` ghi đúng một lần khi có `gather_end`, qua file tạm cùng thư mục rồi thay thế nguyên tử; ngất ghi kho rỗng; chạm `--ticks` trước `gather_end` thì giữ nguyên file đích; ghi theo id, đủ chính xác để đọc lại; `gather_end.data.inventory` cùng schema | 1 | `test_ngat_ghi_kho_rong`, `test_ban_giao_file_va_quan_doc_lai` |
| AC-P3-07 | Smoke bàn giao: fixture `fresh: 100` + `interact` ở frame 0 → `quan --inventory <file> --ticks 0` có id, kind, độ tươi khớp file | 1, Scenario | `test_ban_giao_file_va_quan_doc_lai`; bằng chứng `docs/proof/phase-3/` |
| AC-P3-08 | Trong `day`, bàn giao ngay trong tick chuyển pha, hàng không hao thêm, ca quán chạy từ bước sau; kho quán nhận đủ số lượng, id, độ tươi, kể cả hàng ươn; sức chứa chỉ áp lên giỏ | 1 | `test_phase3.Day`; smoke `day` |
| AC-P3-09 | Giữ chỗ theo id: mỗi loại lấy cá thể khả dụng tươi nhất, hòa thì theo id. Phần giữ có hàng vừa ươn → nhả toàn bộ phần giữ của đơn, thử giữ lại đúng một lần (theo `order_tick` rồi id bàn); không đủ → `unfulfillable` | Bảng giữ chỗ | `test_hang_giu_vua_uon_thi_giu_lai`, `test_giu_lai_duoc_khi_con_hang_tuoi`, `test_khong_giu_hang_uon` |
| AC-P3-10 | Bắt đầu nấu thì tiêu đúng các id đang giữ, chốt `base_price = floor(giá niêm yết × trung bình fresh / 100)`; boa `floor(tiền món × 0.2)` trên giá đã chốt; điểm vẫn là `earned + 100 × floor(reputation)` | Bảng giá | `test_giu_tuoi_nhat_va_gia_theo_tuoi` |
| AC-P3-11 | Thứ tự trong tick theo TICKET-03 (gather: hao tươi ở đầu bước; quán: hao tươi → `spoiled` → giữ lại → bếp → tương tác → thanh toán → khách) | Thứ tự trong tick | `test_phase3` + regression |
| AC-P3-12 | Scenario v1.2: `gather.hold`, `quan.stock` là mảng cá thể; `customers[].reserved` là mảng id; id vật lý duy nhất giữa các nơi chứa; phần giữ phải trỏ tới hàng chưa ươn, đủ công thức, không dùng chung; bỏ `reserved` thì tự cấp; sai hoặc mâu thuẫn → mã 2 | Scenario | `test_kho_dem_va_sai_schema_ma_2`, `test_khong_giu_hang_uon` |
| AC-P3-13 | JSONL: snapshot `hold`, `stock` (quán và Shop), `customers[].reserved` theo schema mới; `cook_started.data.items` sắp theo kind rồi id; `lost` trong `monster_hit`/`faint` là mảng cá thể theo thứ tự bỏ LIFO; dung sai độ tươi ±0.01 | JSONL | `test_phase3`, `test_phase2` |
| AC-P3-14 | HUD cho người chơi đọc được độ tươi hoặc nhận ra hàng ươn | HUD | Chơi thử: thanh độ tươi dưới ô giỏ, gạch chéo hàng ươn |
| AC-P3-15 | Mở rộng (nhóm 6 cần ≥ 2 mục cả buổi): `burn`, `net` khai trong `extensions`, có test và bằng chứng trong README | 2 | `test_ext_burn_net`, `test_extensions_manifest` (có từ tag `phase-4`) |
| AC-P3-16 | CHANGELOG ghi breaking change, schema mới, cách cập nhật fixture; regression P1–P2 còn hiệu lực đạt; test đổi có lý do | 3, DoD | `CHANGELOG.md`, commit `e0f00c2` |
| AC-P3-17 | `docs/verification/phase-3.md` và `docs/proof/phase-3/` khớp commit tag; clarify, nhật ký AI, retro cập nhật | DoD | QA, PO |

Không làm: Chợ Chú Sáu, Dòng nước lũ (`current`), Khách đặt trước (`reservations`). Xem [clarify #20](../clarify.md).

## Rủi ro đã gặp
- Một người (Lead) ôm cả adapter, lặn, quán, `day` và HUD: tích hợp nhanh, nhưng phần đóng góp Phase 3 của các bạn khác ít. Retro P4 cần nêu.
- `tests/helpers.py` và `tests/test_smoke_p1.py` vốn là file "không sửa" nhưng phải sửa để chuyển fixture: lý do ghi trong CHANGELOG và clarify #19.
- Chưa có `docs/verification/phase-3.md` và `docs/proof/phase-3/` (QA cần bổ sung, dựa trên commit tag `e4daaf4`).
