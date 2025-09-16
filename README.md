# Task Manager

## Giới thiệu
Task Manager là ứng dụng web giúp quản lý công việc, sự kiện, phân công nhiệm vụ và thông báo. Backend sử dụng Django REST Framework, đã được deploy tại:

**URL:** https://nguyentukien-task-manager.onrender.com

## Các API Endpoint chính

### Xác thực
- POST /login/ — Đăng nhập
- POST /signup/ — Đăng ký
- POST /logout/ — Đăng xuất
- GET /me/ — Lấy thông tin người dùng hiện tại

### Công việc (Tasks)
- GET, POST /tasks/ — Danh sách & tạo công việc
- GET, PATCH, DELETE /tasks/<id>/ — Chi tiết, cập nhật, xóa công việc
- POST /tasks/<id>/notify/ — Gửi thông báo công việc
- POST /tasks/<id>/check/ — Đánh dấu hoàn thành

### Phân công (Assignments)
- GET, POST /assignments/ — Danh sách & tạo phân công
- GET, PATCH, DELETE /assignments/<id>/ — Chi tiết, cập nhật, xóa phân công
- POST /assignments/<id>/complete/ — Đánh dấu hoàn thành

### Sự kiện (Events)
- GET, POST /events/ — Danh sách & tạo sự kiện
- GET, PATCH, DELETE /events/<id>/ — Chi tiết, cập nhật, xóa sự kiện
- POST /events/<id>/invite/ — Mời tham gia sự kiện
- GET /events/<id>/count_guests/ — Đếm số khách
- POST /events/<id>/send_reminder/ — Gửi nhắc nhở
- POST /events/<id>/update_status/ — Cập nhật trạng thái
- DELETE /events/<id>/cancel/ — Hủy sự kiện

### Lời mời (Invitations)
- POST /invitations/<id>/accept/ — Chấp nhận lời mời
- POST /invitations/<id>/decline/ — Từ chối lời mời

### Ghi chú (Notes)
- GET, POST /notes/ — Danh sách & tạo ghi chú
- GET, PATCH, DELETE /notes/<id>/ — Chi tiết, cập nhật, xóa ghi chú

### Thông báo
- GET /notifications/ — Danh sách thông báo
- POST /notifications/<id>/mark_read/ — Đánh dấu đã đọc
- POST /notifications/mark_all_read/ — Đánh dấu tất cả đã đọc

### Người dùng
- GET /users/ — Danh sách người dùng

---

Dự án phát triển bởi Nguyễn Tử Kiên. Mọi góp ý xin liên hệ qua email hoặc GitHub.
