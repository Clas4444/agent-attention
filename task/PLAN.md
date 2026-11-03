# Gói việc agent-attention — kiểm định trục, quota và baseline

Owner chat: Kiểm tra repo Agent attention.
Repo độc quyền sửa: this repository.
Đọc README.md và EVIDENCE-CONTRACT.md trong task trước, rồi repo AGENTS/map.

| ID | Ưu tiên | Việc cần làm | Tiêu chí hoàn tất |
|---|---|---|---|
| AT-01 | P0 | Audit ba dataset attention/combined/grid và original-vs-functional | Reproduce counts/metrics, exact-source false FAIL riêng, grid partial đúng denom |
| AT-02 | P0 | Sửa harness stop/resume/quota và semantics | Stop first capacity event, shared marker, retry append-only, NOT_RUN explicit; first partial quota không relabel pre-action |
| AT-03 | P0 | Loại treatment leakage, strengthen oracle | Baseline không payload/cue/profile; protect skill+case+extra files; functional invariants/mutation checks |
| AT-04 | P1 | Pilot single-axis đúng điều khiển với tối đa24 CLI | 5 trục × mức1/5, bốn trục còn lại3 + balanced =11 profiles; matched baseline/attention =22; thêm balanced pair ca thứ2 =24 |
| AT-05 | P1 | Quan sát behavior và profile restore | Log actual read/edit/check/reconcile per context; no state-write compliance proxy; unknown fact dừng không edit |
| AT-06 | P1 | Evidence, figures, publish và CI | Hashes/dataset/scripts/charts đồng bộ trong commit, không claim completed grid hay token monotonic |

## Thiết kế thí nghiệm cụ thể

Chọn dependencies/multi-file hoặc một task khó hơn cents làm ca chính nếu phù hợp
với oracle kiểm được. 11 cấu hình: baseline3/3/3/3/3, rồi từng trục riêng1 và5,
bốn trục khác giữ3. Với mỗi cấu hình, ghép một no-skill baseline mới và một attention
run:22 CLI; thêm một cặp balanced trên ca thứ2:2 CLI. Cố định seed và đảo thứ tự
hai nhánh, không luôn baseline trước. Không randomize sau khi thấy outcome.
N=1 mỗi condition là pilot descriptive, không đủ CI đáng tin cho per-axis effect;
có thể chọn thiết kế nhỏ hơn để giữ budget và ghi phần chưa đo. Trước khi gọi phải
khẳng định cả mức1 và5 xuất hiện ở focus, tránh lưới cũ chỉ focus1. Không chạy243
profiles, không tự resume688 ô, không tự retry152 BLOCKED. Nếu quota chặn dừng cả
hai chat qua marker; hoàn tất offline remediation và phân tích lịch sử.

Balanced không có override directives; mức thấp chỉ giảm discretionary work,
không bỏ mandatory/risk-triggered checks. Mức cao không thêm vòng vô ích. Task và
quality oracle giữ như nhau. Nếu cần kiểm conditional restore thêm deterministic
checks, không gọi model ngoài24. Behavior evidence có read coverage, intermediate
checks, actual risk-triggered work, reconciliation before dependency; không đồng
nhất usage/token với proof of adherence. Không đổi semantics chỉ để giảm token.

## Figures tối thiểu

1. Grid cũ progress132/152/688 và coverage5trục với missingness, không full factorial claim.
2. Paired token/time deltas và scatter baseline/attention, chỉ subset valid pairs.
3. New per-axis1/3/5 pilot plot, trục khác3, sample-size/case và uncertainty limits.
4. Acceptance/policy/integrity đi kèm cost; restore/conditional behavior trace nếu có.
Mean-of-pair-percent và ratio-of-means tách riêng; đối chiếu PDF time discrepancy.
Không vẽ đường mục tiêu hypothetical vào observed series.

## Hoàn tất và phạm vi

P0 tests -> freeze -> pilot -> analyze/plot -> full suite/assets/links/hash -> push.
Cập nhật TASK-STATUS.md, xuất dữ liệu/chart script trong repo, raw logs .loop.
Không sửa workflow repo/parent maps/global skill; nếu cần graph shared compatibility
chỉ read frozen workflow source và báo mismatch, không tự đồng bộ repo kia.
Push luôn phải kèm evidence/biểu đồ và ghi NOT_RUN/BLOCKED trung thực.
