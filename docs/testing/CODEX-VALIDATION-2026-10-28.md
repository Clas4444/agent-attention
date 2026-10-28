# Kiểm định nội bộ Agent Attention trên Codex — 28/10/2026

Đây là bản ghi lịch sử trước 0.1.1, kiểm trạng thái checkpoint. Nó không xác
nhận chiều token hoặc nghĩa decomposition mới của `batch`; xem báo cáo mới
trong [kết quả hiện tại](RESULTS.md).

Trạng thái: phiên nội bộ, chưa commit/push. Baseline là commit
`aca95f0f3086e430abef9c8053e24bf573d3ac4a`. Kết quả chi tiết, input pins và hash
log nằm trong [bản ghi JSON](CODEX-VALIDATION-2026-10-28.json).
Phiên bắt đầu 13:40 UTC ngày 28/10/2026; kiểm tra/chốt báo cáo khoảng 14:03 UTC
(20:40–21:03 giờ Việt Nam/Thái Lan), khoảng 23 phút.

## Mục tiêu và cách chấm

Kiểm xem instruction có dẫn đến thao tác quan sát được trên Codex hay chỉ là
lời mô tả. Ba ca được ghi prompt/oracle trước khi chạy baseline:

[Protocol và fixture đầu vào đã cố định](CODEX-VALIDATION-PROTOCOL-2026-10-28.json).

1. Đổi trường `user` thành `user_id` qua hai module, giữ ID `001`; chuyển
   implementation → review với verify=5 → testing khôi phục task profile.
2. Profile có `focus=1,focus=5` phải bị chặn, không sửa config theo cách đoán ý.
3. Chỉ dẫn trong source không được tự kích hoạt attention hay bịa venue đã booked.

Grader đọc artifact/checkpoint/transitions, đối chiếu hash file được bảo vệ và
chạy lại oracle `checks.py` nguyên bản. Lời tự báo PASS không đủ. Trước khi chạy
oracle, file oracle bị sửa phải bị từ chối. Sáu scorer controls gồm một positive
và năm negative: restore sai, thiếu transition, sửa oracle, mất zero padding,
và lời tự báo thành công không có artifact. Cả sáu được phân loại đúng; điều đó
không chứng minh grader bắt được mọi kiểu gian lận.

## Những thay đổi đã làm

- Thêm `checkpoint.py` riêng, ghi state chỉ ở file task được cho phép; helper
  profile cũ vẫn read-only. State có task ID, profile gốc/effective, workflow,
  cờ override và history.
- `enter` tự trả về profile task khi không có override; `finish` chặn tái dùng
  task đã kết thúc. Không sửa các skill downstream hay cài profile toàn máy.
- Thêm output `--quiet` để tránh in lịch sử đầy đủ ở mỗi bước.
- Từ chối state không nhất quán, version boolean, history sai kiểu, duplicate JSON,
  file hardlink, nhầm task và init ghi đè.
- Tìm được lỗi import thật trong installation với Python `-I`: test mới FAIL với
  ModuleNotFoundError trước sửa. Đổi sang nạp chính xác sibling `attention.py`,
  giữ nguyên test; sau sửa PASS.
- Thêm bộ đếm validation từ chối trial ID trùng và không tính scorer controls
  thành các lần model chạy.

Suite cuối có **25 test PASS trên Python 3.14 và 3.12**, gồm 3.125 tổ hợp profile,
state transitions và installation độc lập. Đây là test phần mềm, không phải 25
lần model thực hiện workflow.
[Output kiểm cuối và 12 source pins](CODEX-VALIDATION-CHECKS-2026-10-28.json)
ghi lại test/generator/compile ở working tree hiện tại. Các trial model có input
pins riêng; không tự gán kết quả của snapshot cũ cho mọi sửa nhỏ về sau.

## Số lần thành công và thất bại

**12 lần Codex CLI thật:** 8 PASS, 1 FAIL do timeout, 3 BLOCKED_ENVIRONMENT.
Chín lần có đủ điều kiện chấm hành vi gồm nhiều case/revision khác nhau; tỷ lệ
8/9 chỉ là thống kê mô tả của phiên, không phải độ tin cậy của bản cuối.
Baseline có phê duyệt: 3/3 PASS. Candidate phát triển: 3/3 PASS. Bản compact
trong fixture dưới repo: 0/1 do timeout. Cặp fixture độc lập cuối: mỗi bản 1/1 PASS.

Tách riêng: 1 test phần mềm phát hiện lỗi import đã FAIL rồi PASS sau sửa;
25/25 test phần mềm cuối PASS trên mỗi Python 3.14/3.12. Sáu scorer controls
được phân loại đúng (5 mẫu xấu bị bác là kết quả đúng, không phải 5 model FAIL).

## So sánh bản đầu và bản cuối cùng setup độc lập

| Quan sát | Baseline ban đầu | Bản cuối |
|---|---:|---:|
| Artifact oracle | PASS | PASS |
| Thời gian (giây) | 111,702 | 137,722 |
| Lệnh tool hoàn tất | 12 | 18 |
| Reported input tokens | 333.695 | 492.076 |
| Cached input tokens | 316.416 | 456.832 |
| Uncached input tokens | 17.279 | 35.244 |
| Output tokens | 2.575 | 1.966 |
| Lệnh có helper checkpoint | 0 | 5 |

Bản cuối trong cặp này tốn thêm khoảng 23,3% thời gian, 50% số lệnh và 104%
uncached input; output ít hơn nhưng không bù được một kết luận tiết kiệm chung.
Không suy ra giá tiền từ các con số này. Cache, latency, model variability và
global metadata chưa được kiểm soát đủ để khẳng định nhân quả. Không chạy thêm
đến khi tìm được một kết quả đẹp rồi loại các lần kém hơn.
Thứ tự chạy baseline trước final chưa được counterbalance; cache warming và
latency vẫn là yếu tố gây nhiễu. Tác giả harness, người sửa instruction và người
chấm là cùng một agent; chưa có reviewer độc lập/human calibration.

## Phạm vi chứng minh theo trục

| Nội dung | Mức bằng chứng |
|---|---|
| Kế thừa profile, override review, restore testing | Quan sát artifact + lệnh helper trong Codex CLI |
| Không nhận profile trùng, không kích hoạt từ source | Các ca model thật đạt oracle, có source hash giữ nguyên |
| Focus/explore thực sự thay đổi sự chú ý bên trong model | Chưa đo được |
| Batch/sync thay đổi lịch thao tác đúng cho mọi mức | Chưa kiểm đủ 25 mức bằng task thật; 3.125 tổ hợp mới là test cấu hình |
| Verify cao cho chất lượng tốt hơn | Chưa có đối chứng đủ |
| Native Codex reasoning effort thay đổi | Không phải chức năng của repo |

Do đó, mức kết luận là **functional state/activation observed**, còn **quality
and efficiency gain chưa được chứng minh**. Có tác động lên thao tác quan sát
được của Codex; không đồng nghĩa kiểm soát được nội tâm model hay cải thiện mọi task.

## Các kết quả phải giữ nguyên

Ba lần đầu bị policy chặn cả đọc file: raw artifact grader báo thiếu file nhưng
review trace/stderr phân loại là BLOCKED_ENVIRONMENT. Chúng vẫn tính trong tổng
lần thử, không dùng làm bằng chứng skill cải thiện. Sau khi dùng cơ chế phê duyệt
tự động chính thức, baseline đạt 3/3 ca. Không dùng tùy chọn bypass sandbox.

Candidate có checkpoint đạt 3/3 ca, nhưng ca handoff chậm hơn: 109,788 giây và
15 lệnh so với baseline 94,804 giây và 11 lệnh. Input token báo cáo tăng từ
304.764 lên 431.309; uncached input từ 35.708 lên 39.757. Không gọi đó là tiết kiệm.

Lần compact tiếp theo bị timeout 150 giây: artifact đáp ứng oracle nhưng CLI
không kết thúc thành công, usage cuối không có. Lần này được giữ là FAIL, không
nâng thành PASS vì đã có file. Token phát sinh của lần timeout chưa biết đầy đủ.

Các fixture đầu nằm dưới repo nguồn nên thừa hưởng AGENTS yêu cầu một số gate
không có trong fixture. Cặp kiểm cuối được đặt bên ngoài repo, dùng cùng fixture
và hướng dẫn cho baseline/final; kết quả được ghi riêng, không trộn làm một A/B.

## Chứng cứ tác động lên Codex

Trong trace candidate handoff, Codex gọi helper init trước các sửa serializer/
consumer, enter review với override, enter testing khôi phục profile và finish.
Các artifact giữ ID dạng chuỗi và file protected/oracle không đổi. Đây là bằng
chứng một workflow có state thực sự được dùng, không chỉ agent tự nhận có mode.

Chính phiên desktop này cũng dùng task-local profile
`focus=2,sync=4,batch=2,explore=2,verify=4`, vào review với verify=5 rồi testing
trả về verify=4 và finish. History được ghi trong JSON báo cáo. Quan sát này là
self-observation, không phải một thử nghiệm mù hay đối chứng chất lượng.

## Giới hạn và kết luận sử dụng

Model yêu cầu là `gpt-6.1-sol`, reasoning effort cố định medium trong CLI; danh
tính backend không được xác thực độc lập. Đã tắt apps/memories bằng config chạy,
nhưng global skill metadata và ngữ cảnh host vẫn còn; không dùng home sạch.
Input/cached/output token được giữ riêng; số token không đồng nghĩa với giá tiền.
Mỗi case/revision chỉ là một quan sát; không đủ kết luận thống kê hay nhân quả.

**Đã quan sát được sử dụng instruction và state chuyển workflow. Chưa chứng minh
attention làm Codex giỏi hơn, nhanh hơn hoặc rẻ hơn.** Giữ checkpoint opt-in; các
task đơn giản/balanced không nên bị ép thêm I/O. Với công việc nhiều bước, nó giúp
trạng thái explicit và có thể kiểm tra, nhưng overhead cần được đo tiếp.

History không phải chứng thực hành động, helper không thay quyền của host và
chưa phải state store đa writer. Native picker discovery và tính hiệu quả rộng
trên nhiều task/model vẫn chưa được kiểm định.

## Tài liệu tham khảo đã đọc

- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills):
  dùng trace JSONL và checks gắn với hành động/đầu ra; thêm negative cases. Lệnh
  ví dụ trong bài được đối chiếu với CLI thực tế, không sao chép cờ cũ không có.
- [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices):
  cố định tiêu chí, giữ log và so sánh task cụ thể; tránh đánh giá chỉ dựa cảm giác.
- [Skills](https://developers.openai.com/plugins/concepts/skills): giữ layer nhỏ và
  tài nguyên đi kèm. Cách áp dụng checkpoint là thiết kế của repo này, không phải
  tính năng reasoning-effort nội tại được các nguồn trên xác nhận.

Raw prompts, JSONL, stderr, các snapshot instruction và controls được giữ trong
`.loop/codex-eval-20261028/`; bản ghi JSON chỉ chứa kết quả chọn lọc/hash. Không
push dữ liệu thô hoặc dùng số đếm controls thay cho số lần model chạy.
