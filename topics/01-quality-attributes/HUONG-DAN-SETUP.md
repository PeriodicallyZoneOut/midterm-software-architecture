# HƯỚNG DẪN SETUP & TRIỂN KHAI TOÀN BỘ CHỦ ĐỀ 01
## QUALITY ATTRIBUTES: SCALABILITY & SECURITY
### (ONLINE BOUTIQUE + LOCUST WORKLOAD & SCRIPTHAMMER SECURITY AUDIT)

- **Người phụ trách**: **Nhật Anh** (Chủ đề 01 - Quality Attributes)
- **Thư mục làm việc (Working Dir)**:  
  `d:\VScode\midterm-software-architecture\topics\01-quality-attributes`

---

## 📋 TỔNG QUAN CÁC FILE LIÊN QUAN ĐẾN SETUP & DEMO

| Tên File | Vai trò |
|---|---|
| 📄 [**`setup-and-run.ps1`**](setup-and-run.ps1) | **Script PowerShell tự động hóa 1-Click** (kiểm tra cluster, workloads, port, scale, kiểm tra tải Locust, và audit ScriptHammer). |
| 📄 [**`CHEAT-SHEET-CMD.md`**](CHEAT-SHEET-CMD.md) | File tóm tắt lệnh thao tác nhanh 1 trang dành cho buổi vấn đáp. |
| 📄 [**`KICH-BAN-DEMO-CHAT-LUONG.md`**](KICH-BAN-DEMO-CHAT-LUONG.md) | Kịch bản thuyết minh và thao tác chi tiết từng phút (Scalability 5 phút + Security 5 phút). |

---

## 🚀 HƯỚNG DẪN 4 BƯỚC SETUP TỪ ĐẦU ĐẾN CUỐI

### BƯỚC 0: ĐIỀU KIỆN TIÊN QUYẾT (DOCKER DESKTOP KUBERNETES)
1. Mở **Docker Desktop**.
2. Kiểm tra biểu tượng Kubernetes ở góc dưới bên trái có màu xanh: **`Kubernetes running`**.
3. Nếu chưa bật: Bấm **Cài đặt ⚙️ (Settings)** $\rightarrow$ **Kubernetes** $\rightarrow$ Tích `[v] Enable Kubernetes` $\rightarrow$ **Apply & restart**.

---

### BƯỚC 1: KIỂM TRA HỆ THỐNG BẰNG 1 CLICK

Mở **PowerShell**, di chuyển vào thư mục Chủ đề 01:
```powershell
cd d:\VScode\midterm-software-architecture\topics\01-quality-attributes
.\setup-and-run.ps1 -CheckOnly
```

> **Kết quả kỳ vọng**:
> - Cụm Kubernetes hiển thị `Ready`.
> - Các Pods của Online Boutique (`frontend`, `cartservice`, `checkoutservice`, `productcatalogservice`, `recommendationservice`, `loadgenerator`) đều ở trạng thái `Running`.
> - Phản hồi HTTP tới `http://localhost` trả về mã `200 OK`.
> - Xuất bảng thống kê tải thời gian thực từ Locust (`loadgenerator`).

*(Nếu cụm máy của bạn là máy mới chưa có Pods Online Boutique, chỉ cần chạy `.\setup-and-run.ps1` để tự động deploy toàn bộ manifest `projects\online-boutique\source\release\kubernetes-manifests.yaml`).*

---

### BƯỚC 2: TRUY CẬP ỨNG DỤNG ONLINE BOUTIQUE

Mở trình duyệt Web truy cập:
- **URL chính thức**: `http://localhost`
- *(Trường hợp Docker Desktop không bind cổng 80, mở tab PowerShell chạy: `kubectl port-forward svc/frontend 8080:80` rồi truy cập `http://localhost:8080`).*

Thao tác kiểm tra tính toàn vẹn nghiệp vụ:
1. Xem danh mục sản phẩm (Browsing Products).
2. Chọn sản phẩm $\rightarrow$ Đổi tiền tệ (USD, EUR, JPY).
3. Bấm **Add to Cart** $\rightarrow$ Xem giỏ hàng.
4. Bấm **Place Order** $\rightarrow$ Nhận trang xác nhận đơn hàng thành công.

---

### BƯỚC 3: THỰC NGHIỆM ĐO LƯỜNG SCALABILITY & TẢI LOCUST

Hệ thống đã tích hợp sẵn container `loadgenerator` đóng vai trò Locust Client liên tục bắn tải đa tiến trình vào hệ thống.

#### 3.1. Xem bảng thống kê tải thời gian thực (RPS, Latency p50/p95/p99, Failures):
```powershell
.\setup-and-run.ps1 -CheckLocust
# Hoặc xem log trực tiếp dạng stream:
kubectl logs deployment/loadgenerator -c main --tail=20 -f
```

#### 3.2. Nâng tải (High Workload Injection) để tạo áp lực lên hệ thống:
```powershell
.\setup-and-run.ps1 -SetLoadHigh
```
*(Lệnh này nâng số người dùng mô phỏng từ 10 lên 50 users với spawn rate 5 users/giây).*

#### 3.3. Thực hiện Horizontal Scaling Pod để giải quyết Bottleneck:
Khi frontend chịu tải cao, mở rộng số lượng Pod frontend từ 1 lên 3:
```powershell
.\setup-and-run.ps1 -ScaleFrontend
```
Kiểm tra 3 Pod frontend chia tải:
```powershell
kubectl get pods -l app=frontend
```

#### 3.4. Đưa hệ thống về trạng thái ban đầu sau khi kết thúc thí nghiệm:
```powershell
.\setup-and-run.ps1 -ResetScale
.\setup-and-run.ps1 -SetLoadBaseline
```

---

### BƯỚC 4: KIỂM CHỨNG BẢO MẬT SCRIPTHAMMER (SECURITY AUDIT)

Dự án thứ hai trong Chủ đề 01 là **ScriptHammer** (Next.js + Supabase + Stripe) dùng để minh chứng các thuộc tính Bảo mật (Threat Modeling, Row Level Security, Anti-Enumeration, Secret Leak Prevention).

Chạy lệnh kiểm tra nhanh cấu hình bảo mật:
```powershell
.\setup-and-run.ps1 -AuditSecurity
```

Các vị trí mã nguồn trọng tâm cần mở sẵn trên VS Code để chỉ điểm cho Hội đồng:
1. **Chống lộ lọt bí mật mã nguồn (SAST Secret Scanning)**:  
   [`projects/scripthammer/source/.gitleaks.toml`](projects/scripthammer/source/.gitleaks.toml)
2. **Kiểm soát truy cập dữ liệu tầng Database (Supabase Row Level Security)**:  
   [`projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql`](projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql#L1220-L1230)
3. **Chống vét cạn tài khoản & dò quét danh tính (Account Enumeration Defense)**:  
   [`projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts`](projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts#L20-L42)
4. **Xử lý danh tính OAuth an toàn (PKCE & Display Name Cascade)**:  
   [`projects/scripthammer/source/src/lib/auth/oauth-utils.ts`](projects/scripthammer/source/src/lib/auth/oauth-utils.ts#L25-L50)
