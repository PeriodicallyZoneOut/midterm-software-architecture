# CHEAT SHEET LỆNH DEMO — CHỦ ĐỀ 01: QUALITY ATTRIBUTES
## NHẬT ANH — SCALABILITY (ONLINE BOUTIQUE) & SECURITY (SCRIPTHAMMER)

- **Thư mục làm việc**: `d:\VScode\midterm-software-architecture\topics\01-quality-attributes`

---

## ⚡ 1. LỆNH CHUẨN BỊ TRƯỚC GIỜ VẤN ĐÁP (PRE-DEMO)

```powershell
# Di chuyển vào thư mục Chủ đề 01
cd d:\VScode\midterm-software-architecture\topics\01-quality-attributes

# Kiểm tra toàn diện hệ thống bằng 1 click
.\setup-and-run.ps1 -CheckOnly

# (Nếu cần) Mở cổng truy cập frontend nếu chưa map trực tiếp vào cổng 80:
kubectl port-forward svc/frontend 8080:80
```
- Mở trình duyệt Web: `http://localhost` (hoặc `http://localhost:8080`).

---

## 🚀 2. KỊCH BẢN 1: SCALABILITY & TẢI LOCUST (ONLINE BOUTIQUE — 5 PHÚT)

### 2.1. Soi bảng thống kê tải thời gian thực (Baseline 10 users):
```powershell
.\setup-and-run.ps1 -CheckLocust
# Hoặc stream trực tiếp:
kubectl logs deployment/loadgenerator -c main --tail=15 -f
```
- *Giải thích*: Chỉ số **RPS** (Requests/second), **Latency** (Avg/Med/Max) và tỷ lệ lỗi **Failures (0.00%)**.

### 2.2. Đẩy tải lên mức cao (Stress test với 50 users, 5 spawn rate):
```powershell
.\setup-and-run.ps1 -SetLoadHigh
```
- Quan sát độ trễ (latency) tăng đột biến do tài nguyên frontend bị bão hòa (Resource Saturation & Bottleneck).

### 2.3. Thực thi Horizontal Pod Autoscaling/Scaling (Giải quyết Bottleneck):
```powershell
.\setup-and-run.ps1 -ScaleFrontend
# Kiểm tra 3 Pod frontend đang sẵn sàng:
kubectl get pods -l app=frontend
```
- Quan sát độ trễ bình ổn trở lại, RPS tăng lên tương ứng theo Định luật Little (Little's Law: $L = \lambda W$).

### 2.4. Reset hệ thống về trạng thái ban đầu:
```powershell
.\setup-and-run.ps1 -ResetScale
.\setup-and-run.ps1 -SetLoadBaseline
```

---

## 🛡️ 3. KỊCH BẢN 2: SECURITY AUDIT & BẢO MẬT (SCRIPTHAMMER — 5 PHÚT)

### 3.1. Chạy lệnh tóm tắt kiểm toán bảo mật:
```powershell
.\setup-and-run.ps1 -AuditSecurity
```

### 3.2. Mở 4 file trọng tâm trên VS Code và đối chiếu kiến trúc:

1. **Chống lộ lọt khóa API / Secret (SAST & Pre-commit scan)**:
   - File: [`projects/scripthammer/source/.gitleaks.toml`](projects/scripthammer/source/.gitleaks.toml)
   - *Điểm nhấn*: Định nghĩa regex rules phát hiện Stripe Secret Key, Supabase Service Role Key và chặn commit trước khi đẩy lên remote repo.

2. **Kiểm soát truy cập dữ liệu tầng CSDL (Supabase Row Level Security - RLS)**:
   - File: [`projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql`](projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql#L1220-L1230)
   - *Điểm nhấn*: `ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;` kết hợp các Policy bảo đảm nguyên tắc Least Privilege (người dùng chỉ xem/sửa bản ghi của chính mình qua `auth.uid()`).

3. **Chống dò quét tài khoản & Brute-force (Anti-Enumeration Rate Limiting)**:
   - File: [`projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts`](projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts#L20-L42)
   - *Điểm nhấn*: Hàm `authRateLimitMessage` trả về cùng thông điệp generic `EMAIL_QUOTA_MESSAGE` ngăn chặn kẻ tấn công dò tìm xem email có tồn tại trong hệ thống hay không.

4. **Xử lý danh tính OAuth an toàn (OAuth Metadata Sanitization)**:
   - File: [`projects/scripthammer/source/src/lib/auth/oauth-utils.ts`](projects/scripthammer/source/src/lib/auth/oauth-utils.ts#L27-L50)
   - *Điểm nhấn*: Hàm `extractOAuthDisplayName` fallback cascade chống null/khoảng trắng rỗng và loại bỏ nguy cơ injection.
