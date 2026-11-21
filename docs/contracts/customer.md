# Schema khách (Quán, lát 3)

> Chủ: @viethoang127. Người dùng: @minhthu27 (`quan.py`, `quan_service.py`), @Kaylez-TXL (test hộp đen).
> Nguồn: PRD-0 mục D (scenario), E (JSONL), F (luật một bước). Chỗ nào PRD **không nói rõ** thì ghi "Giả định" và liệt kê ở mục 7.
> Đổi schema sau khi đã gộp: báo cả nhóm, ghi lý do ở cuối file.

Khách là phần tử của `sim.customers`, xuất nguyên trong `snapshot()["customers"]` (sắp theo `id`, **chỉ liệt kê khách còn ngồi**).
Số liệu (thời gian, giá, tip…) chỉ đọc từ `game.contract.json` → `tuning.quan`, `tuning.menu`.

## 1. Các trường

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `id` | string, duy nhất | Mã khách, cấp bằng `ids.new("C")`; khách từ scenario phải `ids.reserve(id)`. Sắp theo `ids.id_key`. |
| `table_id` | string | Bàn đang ngồi, phải là bàn có thật; **mỗi bàn tối đa một khách**. |
| `dish_id` | string | Món khách chọn, là khóa trong `tuning.menu`. |
| `order_tick` | int ≥ 0 | `phase_tick` lúc khách đến (sau khi tăng). Dùng để chọn đơn cũ nhất. Mặc định `0`. |
| `state` | `"waiting"` \| `"eating"` | Xem mục 2. Mặc định `waiting`. |
| `patience_ticks_left` | int ≥ 0 | Kiên nhẫn còn lại. Mặc định đầy = `patience_s × 60`. |
| `eat_ticks_left` | int ≥ 0 | Thời gian ăn còn lại. Chỉ > 0 khi `eating` (đầy = `eat_s × 60` lúc bắt đầu ăn). Mặc định `0`; **scenario khách `eating` phải khai > 0** (không tự điền đầy). |
| `order_status` | `reserved` \| `assigned` \| `unfulfillable` \| `served` | Trạng thái đơn, xem mục 2. Mặc định `reserved`. |
| `reserved` | object `{kind: n}` | Nguyên liệu đang giữ chỗ (map kind → số lượng). |
| `base_price` | int | Tiền món, chốt **lúc phục vụ**. Bắt buộc khi `eating`; chưa có thì không khai. |
| `tip` | int ≥ 0 | Boa, chốt cùng lúc `base_price`. Bắt buộc khi `eating`. |

Ghi chú: phan-cong.md viết tắt `patience_ticks`, `eat_ticks`, `dish`; tên chính thức theo PRD là `patience_ticks_left`, `eat_ticks_left`, `dish_id`. Payload món (`hand`) là `{order_id, dish_id, base_price}` với `order_id` = `id` khách.

## 2. Giá trị `state` và `order_status`

**`state`** (khách):

| Giá trị | Nghĩa |
|---|---|
| `waiting` | Đang chờ món. Kiên nhẫn giảm mỗi bước. |
| `eating` | Đã được phục vụ, đang ăn. `eat_ticks_left` giảm mỗi bước. Phải có `order_status == "served"`. |

**`order_status`** (đơn của khách):

| Giá trị | Nghĩa | Ràng buộc (vi phạm → mã 2) |
|---|---|---|
| `reserved` | Mới đến, đã giữ nguyên liệu, chưa lên bếp. | `reserved` đúng công thức của `dish_id`; không có món ở bếp/tay. |
| `assigned` | Bếp đã nhận nấu (hoặc món ready / đang trên tay). | `reserved` **rỗng**; có **đúng một** món khớp đơn ở bếp **hoặc** ở tay (không cả hai). Bếp `cooking` thì timer dương. |
| `unfulfillable` | Đơn không làm được, khách vẫn ngồi chờ. | `reserved` rỗng, không có món ở bếp/tay. |
| `served` | Đã bưng món, khách ăn. | `state == "eating"`, timer ăn > 0, có `base_price` và `tip`. |

Khách rời bàn **không phải trạng thái**: khách bị xóa khỏi `customers` (xem mục 3, 5).

## 3. Sự kiện (PRD mục E)

| Sự kiện | `data` | Ai phát | Khi nào |
|---|---|---|---|
| `customer_arrived` | `{order_id, table_id, dish_id}` | `spawn_customers` (@viethoang127) | Khách mới ngồi vào bàn, đã chọn món và giữ chỗ. `order_id` = `id` khách. |
| `no_dish` | `{}` | `spawn_customers` | Đến lượt, **có bàn trống** nhưng không món nào đủ nguyên liệu. Không tạo khách, kho không đổi. |
| `customer_left` | `{order_id, table_id, reason, reputation}` | `tick_customers` (@viethoang127) | `reason = "patience"`: khách `waiting` có kiên nhẫn 0 khi ca còn giờ, uy tín cộng `left_reputation_delta`. `reason = "closing"`: hết ca, khách còn chờ rời, **không trừ uy tín**. `reputation` là uy tín sau thay đổi. |

Do @minhthu27 phát: `cook_started`, `dish_ready`, `dish_picked`, `served`, `paid`, `quan_end`. Khi khách rời, **nhả phần giữ thô**, bỏ món của đơn đang nấu/ready/trên tay (nguyên liệu đã dùng không hoàn lại).

## 4. Chọn bàn, chọn món, giữ chỗ (`spawn_customers`)

- **Lịch**: nếu ca còn giờ, khách đến khi `phase_tick == first_customer_tick`, rồi mỗi `customer_interval_s × 60` tick (`phase_tick` sau khi tăng; lịch tính theo `phase_tick` kể cả khi ca rút ngắn).
- **Bàn**: lấy bàn trống có `id` nhỏ nhất (theo `id_key`). Không còn bàn → **bỏ lượt**, không có sự kiện.
- **Món**: trong 3 món của menu, giữ các món **đủ nguyên liệu khả dụng** = tồn vật lý − phần đang giữ của mọi khách. Duyệt món theo mã Unicode của id. Chọn **đều ngẫu nhiên theo seed** (luồng RNG riêng `rng.get("customer_dish")`). Không có món nào đủ → `no_dish`.
- **Khách mới**: `order_status = "reserved"`, `state = "waiting"`, `reserved` = đúng công thức món, `order_tick = phase_tick` hiện tại, kiên nhẫn đầy.
- **Tham gia từ bước sau**: kiên nhẫn của khách mới bắt đầu giảm ở bước kế tiếp; khách mới chỉ được tương tác từ bước sau.
- `random_customers: false` trong scenario tắt hoàn toàn bước này (vẫn dùng khách fixture). Mặc định `true`.

## 5. Thứ tự một bước (PRD mục F, phần quán)

Bước `k` đọc tick `k`, biến trạng thái `k → k+1`, event ghi tại `k+1`. Phần khách nằm ở các điểm sau:

1. Tăng đồng hồ, giảm timer ca, nấu, ăn và kiên nhẫn. **→ `tick_customers_timers`** (chỉ kiên nhẫn của khách `waiting`; thời gian ăn do lát 4 giảm).
2. Bếp theo id; di chuyển; tối đa một interact. *(@minhthu27)*
3. Theo id bàn: khách ăn xong trả tiền rồi rời bàn ngay. *(@minhthu27 phát `paid`; khách bị xóa)*
4. **→ `customers_leave`, phần rời đi**: nếu ca còn giờ, khách `waiting` có `patience_ticks_left == 0` rời với `reason: "patience"`.
5. Hết ca (`time_left_ticks == 0`): khách còn ăn trả ngay (kể cả vừa được giao món); khách còn chờ rời với `reason: "closing"` và không trừ uy tín; rồi `quan_end`.
6. Nếu còn giờ: **→ `spawn_customers`** (cuối bước).

Lưu ý: phục vụ đúng tick kiên nhẫn về 0 vẫn hợp lệ (interact ở bước 2 chạy trước bước 4).

Hàm trong `chonoi/sim/quan_customers.py` để @minhthu27 gắn vào `quan.py` (tên đã thống nhất với @minhthu27):
```python
tick_customers_timers(sim, events)      # bước 1: chỉ giảm kiên nhẫn khách waiting (lát 4 tự giảm eat_ticks_left)
customers_leave(sim, events)            # sau khi khách ăn trả tiền, trước quan_end: patience (trừ uy tín) / closing
spawn_customers(sim, events)            # bước 6, cuối bước, chỉ khi ca còn giờ
tick_customers(sim, events, phase)      # tên cũ của khung, gọi hai hàm trên theo phase ("timers"/"leave"/"all")
remove_customer(sim, customer)          # khi khách ăn xong, trả tiền, rời bàn (nhả giữ chỗ, bỏ món liên quan)
build_fixture_customers(raw, tuning, stock, stoves, hand)  # __init__: khách từ scenario (kiểm + dựng reserved)
```
`customers_leave` **không** xử lý khách `eating`: @minhthu27 cho khách ăn trả tiền và gọi `remove_customer` trước. Trừ uy tín khi khách `patience` bỏ đi do phía khách (lát 3) làm; lát 4 không trừ.
QuanSim cần có: `phase_tick` (tăng 1 mỗi bước, lịch khách tính theo nó), `random_customers` (từ scenario, mặc định True).

## 6. Scenario `quan.customers[]` (PRD mục D)

- Mỗi phần tử: `{id, table_id, dish_id, order_tick, state, patience_ticks_left, eat_ticks_left, order_status, reserved, base_price, tip}`.
- Mặc định: `state: waiting`, `order_tick: 0`, kiên nhẫn đầy, `order_status: reserved`.
- Thiếu `reserved` ở đơn `reserved` → **cấp theo công thức**, xét khách theo `order_tick` rồi id bàn (khách đứng trước lấy từ kho trước).
- `customers` **thay thế** danh sách mặc định; `[]` là rỗng.
- `stock` gồm cả phần giữ chỗ (tồn vật lý), nên `reserved` cộng dồn của mọi khách không được vượt `stock`.

**Mã 2 (BadInput)** liên quan khách: trường sai/chưa hỗ trợ; id trùng; `table_id` không tồn tại; **hai khách cùng bàn**; `state`/`order_status` ngoài tập giá trị; `dish_id` ngoài menu; `reserved` khác công thức hoặc vượt tồn; đơn `assigned` không có đúng một món (bếp hoặc tay), hoặc `reserved` không rỗng; đơn `unfulfillable` có giữ chỗ hoặc có món; khách `eating` không phải `served`, thiếu timer ăn dương, thiếu `base_price`/`tip`; bộ đếm âm hoặc không nguyên; bếp `cooking` timer không dương hoặc món không khớp đơn; bếp và tay cùng giữ một đơn.
Tham chiếu id (ví dụ `stoves[].dish`) không tự tạo thực thể.

## 7. Giả định / câu hỏi còn mở

PRD không nói rõ các điểm sau; tạm quy ước như bên dưới, cần hỏi trợ giảng nếu muốn chắc:

1. **Kiên nhẫn của khách `eating`**: tạm coi **ngừng giảm** (chỉ `waiting` giảm), vì `served` còn mang `patience_ticks_left` để tính boa.
2. **Thời điểm một đơn thành `unfulfillable`**: PRD chỉ mô tả trạng thái (còn chờ, rỗng giữ chỗ, không món), không nói luật chuyển. Tạm chỉ dùng cho fixture; luật sinh khách không tạo trạng thái này.
3. **Tiền tố id khách**: tạm `C` (`C1`, `C2`…).
4. **`customer_left` lúc closing**: tạm do @viethoang127 phát (cùng chỗ với bước rời), thứ tự theo id bàn. Cần khớp với `quan_end` của @minhthu27 (dọn xong mới `quan_end`).
5. **Tên luồng RNG** `customer_dish`: tạm; chỉ cần cố định để cùng seed cho cùng kết quả.
6. **Khách `unfulfillable`/`assigned`** vẫn bị kiên nhẫn giảm và rời `patience` như khách `waiting` (vì `state` vẫn `waiting`).

## Lịch sử đổi

| Ngày | Đổi | Lý do |
|---|---|---|
| 2026-11-21 | Bản 1 (nháp) | Kickoff, chưa có PRD |
| 2026-11-21 | Bản 2: theo PRD-0 D/E/F | Đổi `dish`→`dish_id`, thêm `order_tick`/`order_status`/`base_price`/`tip`, `state` còn `waiting`/`eating`, bỏ trạng thái `assigned` khỏi `state` (thành `order_status`), sửa tên và `data` sự kiện, thêm thứ tự bước |
