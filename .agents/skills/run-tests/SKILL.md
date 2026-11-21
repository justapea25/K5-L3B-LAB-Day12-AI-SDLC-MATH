---
name: run-tests
description: Chạy toàn bộ unittest, smoke hai tiến trình gather → kho → quán, và kiểm tra cùng seed cho JSONL giống từng byte. Dùng trước khi push/mở PR, sau khi gộp nhánh và trước khi Lead gắn tag phase-n.
---

# run-tests — chạy test và kiểm tra tất định

Chạy từ gốc repo. Đừng sửa test cho xanh khi luật sai (xem `AGENTS.md`).

## 0. Chuẩn bị (một lần)

`headless_cmd` trong `game.contract.json` gọi `python3` ở tiến trình con, nên `python3` phải chạy được.

```bash
python3 --version          # cần 3.10+
```

Trên Windows nếu `python3` không có: cài Python từ python.org hoặc tạo alias `python3` trỏ tới `python`. Trong PowerShell dùng `$env:PYTHONPATH = 'tests;.'` thay cho tiền tố `PYTHONPATH=...`.

## 1. Unittest (bắt buộc)

```bash
PYTHONPATH=tests:. python3 -m unittest discover -s tests -v 2>&1 | tee out-unittest.txt
tail -3 out-unittest.txt   # phải thấy "OK"
```

## 2. Smoke hai tiến trình (PRD-0 mục G)

```bash
T=$(mktemp -d)
echo '{"gather":{"hold":["ca_loc","bong_sung","bong_sung"]}}' > $T/dock.json
echo '{"frames":[{"tick":0,"interact":true}]}' > $T/dock-inputs.json
python3 -m chonoi.headless --mode gather --seed 42 --scenario $T/dock.json --inputs $T/dock-inputs.json --ticks 1 --out $T/gather.jsonl --inventory-out $T/catch.json
python3 -m chonoi.headless --mode quan --seed 42 --inventory $T/catch.json --ticks 0 --out $T/quan.jsonl
cat $T/catch.json                       # {"items":{"bong_sung":2,"ca_loc":1}}
head -1 $T/quan.jsonl | grep -o '"stock":{[^}]*}'
```

Đạt khi `stock` ở snapshot quán tick 0 đúng bằng nội dung `catch.json`.

## 3. Tất định: cùng seed → giống từng byte

```bash
for m in gather quan; do
  python3 -m chonoi.headless --mode $m --seed 1 --ticks 600 --out $T/$m-1.jsonl
  python3 -m chonoi.headless --mode $m --seed 1 --ticks 600 --out $T/$m-2.jsonl
  cmp $T/$m-1.jsonl $T/$m-2.jsonl && echo "$m: giống từng byte"
done
```

## 3b. Từ Phase 2: vòng ngày (`--mode day`, Test Contract v1.1)

```bash
python3 .agents/skills/check-contract/check_contract.py      # số chuẩn v1.3 (lõi v1.1 + freshness + bench/soak)
time python3 -m chonoi.headless --mode day --days 1 --seed 1 --ticks 22200 --out $T/day1.jsonl   # phải ≤ 20 s
tail -1 $T/day1.jsonl          # end: reason "days_complete", days_completed 1
grep -o '"name":"[a-z_]*"' $T/day1.jsonl | sort | uniq -c   # có day_start, day_plan, phase_start ×3, gather_end, quan_end, shop_end
python3 -m chonoi.headless --mode day --days 3 --seed 1 --ticks 66600 --out $T/day3.jsonl
grep -o '"active_upgrades":{[^}]*}' $T/day3.jsonl | uniq     # cấp mua ở Ngày n chỉ hiện từ Ngày n+1
```

QA lưu bằng chứng Phase 2 vào `docs/proof/phase-2/` (`integration.*` cho smoke ở mục 2, `day.*` cho vòng ngày).

## 3c. Từ Phase 3: bàn giao kho cá thể và ngưỡng ươn (v1.2)

```bash
echo '{"gather":{"hold":[{"id":"I1","kind":"ca_linh","fresh":100}],"random_fish":false,"monsters":[]}}' > $T/sc100.json
echo '{"frames":[{"tick":0,"interact":true}]}' > $T/dock.json
python3 -m chonoi.headless --mode gather --seed 1 --ticks 5 --scenario $T/sc100.json --inputs $T/dock.json \
  --inventory-out $T/kho.json --out $T/g.jsonl
cat $T/kho.json                # {"items":[{"id":"I1","kind":"ca_linh","fresh":99.99166…}]} (đã hao 1 bước ở giỏ)
python3 -m chonoi.headless --mode quan --seed 1 --ticks 0 --inventory $T/kho.json --out $T/q.jsonl
grep -o '"stock":[^]]*]' $T/q.jsonl | head -1   # "stock":[{"id":"I1","kind":"ca_linh","fresh":99.992}]: cùng id, kind, fresh (±0.01)
echo '{"gather":{"hold":[{"id":"I1","kind":"ca_linh","fresh":30}],"random_fish":false,"monsters":[]}}' > $T/sc30.json
python3 -m chonoi.headless --mode gather --seed 1 --ticks 1 --scenario $T/sc30.json --out $T/s.jsonl
grep '"spoiled"' $T/s.jsonl    # đúng 1 dòng: tick 1, item_id I1, location hold
echo '{"items":{"ca_linh":3}}' > $T/kho_dem.json
python3 -m chonoi.headless --mode quan --seed 1 --ticks 0 --inventory $T/kho_dem.json --out $T/x.jsonl; echo "mã $?"   # phải là 2
```

## 3d. Từ Phase 4: benchmark và soak (v1.3)

```bash
python3 -m chonoi.bench --seed 42 --duration 30 --out $T/bench.json && cat $T/bench.json   # đủ 5 trường
python3 -m chonoi.soak --seed 7 --days 10 --out $T/soak1.json
python3 -m chonoi.soak --seed 7 --days 10 --out $T/soak2.json
grep -E '"days_completed"|"crashes"' $T/soak1.json          # 10 và 0
diff <(grep -v duration_s $T/soak1.json) <(grep -v duration_s $T/soak2.json) && echo "soak tất định"
```

QA lưu `bench.json`, `soak.json` từ **commit gắn tag** vào `docs/proof/phase-4/`.

## 4. Báo kết quả

- Ghi số test, OK/FAIL và kết quả smoke/tất định vào mô tả PR hoặc commit.
- Test đỏ do luật sai → báo chủ lát (xem bảng trong `docs/plan/phase-n.md`), không tự sửa luật của người khác.
- QA lưu log thật vào `docs/proof/phase-n/` (QA giữ thư mục này).
