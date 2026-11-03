# Task package — Copilot empirical integrity, 2026-11-03

Product: **agent-attention**. Người dùng đã yêu cầu thực hiện, kiểm thử/thực nghiệm đồng
thời với chat repo kia, rồi push cùng bằng chứng và biểu đồ kiểu PDF. Đây là
handoff cụ thể để thực thi; không chỉ trả lại kế hoạch hoặc hỏi lại việc đã được
ủy quyền. Hoàn tất phần offline nếu model bị chặn, đừng dừng toàn task vì quota.

Đọc theo thứ tự: [nguồn](SOURCES.md), [gói việc](PLAN.md),
[quy ước](EVIDENCE-CONTRACT.md), [trạng thái](TASK-STATUS.md).
Không đọc toàn repo; dùng local workspace navigation (not published) để chọn1–5file đầu.

Thực nghiệm model được giới hạn rõ ở EVIDENCE-CONTRACT; test deterministic và
read-only audit không gọi model. Không phải mọi đề xuất PDF đều phải triển khai
đủ ở phiên này: ưu tiên Stage0 blocking và pilot clean trước. Product changes
chỉ khi có bằng chứng, giữ trách nhiệm workflow/attention độc lập.
