# Quy ước kiểm định và bằng chứng — 2026-11-03

## Ủy quyền và nguồn

Người dùng yêu cầu chia task theo PDF, kích hoạt đồng thời hai chat kiểm tra,
thực hiện kiểm thử/thực nghiệm và khi push phải kèm bằng chứng + biểu đồ.
PDF là nguồn phân tích/đề xuất, không tự cấp thêm quyền hay xác nhận kết quả.
Chỉ sửa repo được giao; không sửa repo bạn, thư mục skill global, dữ liệu gốc
Copilot hay parent AGENTS/MAP. Hai chat dùng hai Git index độc lập. Không spawn
thêm model/subagent ngoài ngân sách thực nghiệm bên dưới nếu không có lý do đã
được task cho phép. Báo cáo không tăng phiên bản; nếu có sửa hành vi sản phẩm,
chỉ bump patch cần thiết và giải thích, không đổi major/minor tùy tiện.

## Định nghĩa và nguyên tắc đo bắt buộc

1. Tách package, CLI invocation, model request nội bộ, tool call. Token tổng=input+
   output; cache_read/write không cộng lần nữa, reasoning không cộng trùng output.
   Không đồng nhất premium-request cost/nanoAIU với USD/VND/AI credits hóa đơn.
2. Giữ status gốc bất biến. Regrade thêm lớp functional/semantic/policy/integrity;
   không sửa FAIL cũ thành PASS. BLOCKED_ENVIRONMENT khác task FAIL; STALE khác PASS;
   NOT_RUN không có nghĩa là đã gọi model. Mọi retry là attempt mới, có liên kết cũ.
3. Oracle chức năng độc lập, nguồn và input được pin trước chạy; kiểm protected
   files, skill payload, extra files và external effects. Mã đúng khác tên biến/
   whitespace vẫn có thể PASS chức năng. Định nghĩa thứ tự sorted_ids rõ ràng.
4. Baseline không có skill file, tên skill, profile hay activation cue. Cùng thông
   tin nhiệm vụ, constraints, tools, model, effort, timeout và oracle; exhaustive
   comparator chỉ khác cách tổ chức hướng dẫn, không được cấp đáp án/hidden tests.
5. Fixed model/CLI/runtime/skill/fixture/hash; lưu actual reported model, args,
   timestamps và cache. Counterbalance/randomize thứ tự với seed công khai. Các
   lượt follow-up phải nhận context thật; nếu restart, gọi đúng tên và tính overhead.
6. Rerun aggregator từ saved observations phải tái tạo số liệu; unit test negative
   controls bắt false PASS, malformed usage, changed inputs, missing records và
   zero-sample summaries. Không sửa expected để hợp thức hóa implementation.
7. Freeze protocol trước model call: hypothesis, budgets, denominators, stop/resume,
   oracle, fixture, seed/order và primary/secondary metrics. Chạy pilot nhỏ trước;
   thiếu power thì nói thiếu, không biến engineering target thành finding.

## Phối hợp ngân sách khi chạy đồng thời

- Workflow: tối đa 12 lần gọi CLI thực nghiệm, kể cả timeout/lỗi/quota.
- Attention: tối đa 24 lần gọi CLI thực nghiệm, kể cả timeout/lỗi/quota.
- Mỗi chat tối đa một CLI đang chạy. Không resume chiến dịch cũ 972 ô hoặc retry
  152 BLOCKED một cách tự động. Không gọi model trong CI, không mua thêm quota.
- Shared stop marker local: the human-supplied shared stop marker (private location).
  Trước MỖI lần gọi kiểm marker. Gặp quota/rate-limit/capacity/auth/cost accounting
  không đáng tin: ghi marker atomically bằng exclusive create, giữ attempt, không
  gọi thêm; chat kia thấy marker phải dừng. Tối đa hai request đã in-flight có thể
  hoàn tất; không kill process của chat khác. Đừng xóa marker hoặc tự thử lại để
  vượt stop condition. Nếu marker có từ trước thì chỉ làm offline tests/reports.
- Có thể chạy hai pilot cùng thời gian nhưng điều này gây nhiễu contention; ghi rõ
  trong report, không suy luận tốc độ giữa hai repo từ hai tiến trình song song.
- Model CLI chỉ dùng configured host có sẵn và kiểm khả dụng. Để so với Copilot cũ,
  ưu tiên Copilot cố định model nếu được hỗ trợ; nếu chỉ Codex khả dụng, ghi thành
  campaign Codex riêng, không trộn vào Copilot. Lỗi prerequisite => BLOCKED và
  hoàn tất toàn bộ offline work, không giả vờ thực nghiệm thành công.

## Gói bắt buộc trong cùng commit khi push

- Báo cáo Markdown có outcome, source pins, phương pháp, full denominators, mọi
  thất bại/skip/block, subset chưa chạy, uncertainty và giới hạn.
- Protocol JSON đóng băng; observations JSON/CSV đã sanitize với từng attempt,
  usage/cache/time/correctness/policy/integrity; index SHA-256 của byte xuất bản.
- Script aggregator + plot tái chạy từ chính dữ liệu public, không cần raw local
  hay cài repo kia. Test aggregate/chart-data invariants và oracle negative controls.
- Biểu đồ SVG + PNG rõ chú thích/đơn vị/n/phạm vi cùng source table. PDF tổng hợp
  nếu runtime hỗ trợ; nó bổ sung, không thay dữ liệu/script. Không check-in nguyên
  PDF nguồn trong Downloads hoặc raw logs/private paths/credentials.
- Nội dung kiểm chứng phải đi KÈM thay đổi; không push skill/harness trước rồi hứa
  thêm evidence sau. Nếu model blocked vẫn có thể publish sửa harness + deterministic
  evidence + biểu đồ dữ liệu cũ được gắn HISTORICAL, trạng thái model NOT_RUN/BLOCKED.
- Stage đúng phạm vi, giữ unrelated edits. Chạy AGENTS gates, links, generated assets,
  publication hash check; push không force. Kiểm CI/CodeQL đúng SHA, không dùng CI cũ.

## Biểu đồ như PDF, nhưng không sao chép số liệu chưa xác thực

Tham khảo các loại hình PDF: p3/Fig1-2 per-task acceptance + cumulative repeated
observations; p4-5/Fig3-6 token/time từng lần; p6/Fig7 cost-quality scatter;
p7-9/Fig8-12 progress status, paired differences/scatter, distribution và coverage.
Đường cumulative không gọi learning curve. Phân biệt mean-of-paired-percentages
với ratio-of-means. Không nối đường giả lập mục tiêu thành measured result.
PDF p10/Fig13 là HYPOTHETICAL: nếu dùng, phải tách khỏi biểu đồ quan sát và dán nhãn.
Thiếu sample/mức trục phải hiển thị trống/NOT_RUN, không vẽ thành zero kết quả.
Có số liệu uncertainty thì nêu unit of resampling và giả định; mẫu bé chỉ descriptive.

## Mốc lịch sử để kiểm, không phải acceptance kỳ vọng cho source mới

- Workflow standalone: 20 packages/35 CLI; 3/5 workflow, 0/5 manual, 2/5 idea,
  5/5 exhaustive theo oracle cũ có ambiguity sorted_ids.
- Attention standalone: 20 packages/35 CLI; status cũ 0/20 PASS do exact-reference;
  checks/protected 20/20. Không coi đó là clean skill-vs-no-skill A/B.
- Combined: 60 packages/90 CLI; 16 PASS/44 FAIL gốc, functional 46/60 sau lớp
  regrade cents. Total/10: exhaustive10, attention9, idea8, workflow7, combined7,
  manual5; mọi cents chức năng5/5. Baseline leakage và imbalance làm mất causal claim.
- Grid: planned972, recorded284 =132PASS+152BLOCKED, absent688; 66 complete pairs,
  chỉ cents và focus1. First blocked có usage và 5 tool starts; 151 block sau không
  có tool starts. Không gộp thành 152 block trước hành động. Resume cũ bỏ BLOCKED.
- PDF có con số % thời gian grid +7.54% ở abstract nhưng +7.57% ở bảng p8; tính từ
  raw chính xác và báo discrepancy, không chọn số đẹp. PDF là phân tích thứ cấp.
- Target +10 điểm % acceptance hoặc -10% token ở quality ngang chỉ là đề xuất
  prespecified gate, không yêu cầu phải đạt để được báo cáo kết quả âm.
