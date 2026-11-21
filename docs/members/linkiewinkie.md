# linkiewinkie — phản tư cá nhân (≤ 200 từ)

> Bản nháp, Nguyễn Xuân Khánh Linh xác nhận trước khi gộp.

- **Tôi đã làm:** vai PO và harness AI. Chốt clarify #1–7 ([598c649](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/598c649)), #8–17 ([101a123](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/101a123)), #18–28 cho Phase 3–4. Viết plan Phase 1–4 có AC-P1…P4 ([fc9827e](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/fc9827e), [d656177](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/d656177)). Viết AGENTS.md ([85d9b02](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/85d9b02), [f3cae35](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/f3cae35)), ba skill `run-tests`, `verify-phase`, `check-contract` ([09def3e](https://github.com/justapea25/K5-L3B-LAB-Day12-AI-SDLC-MATH/commit/09def3e)), README, CREDITS.
- **Tôi đã giúp:** QA có danh sách AC để dựng ma trận; Lead có số chuẩn v1.1 dạng script để tự kiểm contract.
- **AI sai ở đâu:** Codex sửa file của người khác; tôi đối chiếu bảng phân công rồi bỏ ra. Khi tôi chuyển nhánh giữa phiên, Claude Code vẫn kết luận "game mới ở Phase 2". Tôi kiểm `git log` và tag trên `origin/main` thì thấy đã có v1.3. AI còn ghi nhầm tag `phase-4` và `v1.0.0` trỏ hai commit khác nhau (lấy mã đối tượng tag); kiểm lại bằng `^{commit}` thì cùng `5e188e7`.
- **Bài học:** luôn kiểm nhánh và commit thật trước khi tin kết luận của AI; chốt tên trường nguyên văn đề từ sớm; giới hạn rõ file agent được sửa.
