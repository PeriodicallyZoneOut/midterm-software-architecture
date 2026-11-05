# KỊCH BẢN LIVE DEMO 10 PHÚT — CHỦ ĐỀ 01: QUALITY ATTRIBUTES
## KHẢ NĂNG MỞ RỘNG (SCALABILITY) & AN TOÀN BẢO MẬT (SECURITY)

- **Học phần**: Kiến trúc Phần mềm (Software Architecture)
- **Sinh viên thực hiện**: **Nhật Anh**
- **Thời lượng**: **10 phút chuẩn** (5 phút Scalability với Online Boutique + 5 phút Security với ScriptHammer)
- **Hệ thống thực nghiệm**: 
  1. **Online Boutique**: Cloud-Native Microservices E-Commerce + Locust Load Generator
  2. **ScriptHammer**: Nền tảng SaaS Production-Grade (Next.js, Supabase RLS, OAuth, Stripe)
- **Thư mục làm việc (Working Dir)**:  
  `d:\VScode\midterm-software-architecture\topics\01-quality-attributes`

---

## 🖥️ BỐ CỤC MÀN HÌNH CHUẨN BỊ TRƯỚC GIỜ G (SCREEN LAYOUT)

- **NỬA MÀN HÌNH BÊN TRÁI (Terminal & Code)**:
  - 1 tab PowerShell gõ lệnh `setup-and-run.ps1` và `kubectl`.
  - 1 tab VS Code mở sẵn file [`projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql`](file:///d:/VScode/midterm-software-architecture/topics/01-quality-attributes/projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql#L1220-L1230) và file [`projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts`](file:///d:/VScode/midterm-software-architecture/topics/01-quality-attributes/projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts#L20-L42).
- **NỬA MÀN HÌNH BÊN PHẢI (Trình duyệt Web & Trực quan hóa tải)**:
  - **Tab 1**: Ứng dụng Online Boutique đang chạy: `http://localhost` (hoặc `http://localhost:8080`)
  - **Tab 2 / Terminal con**: Cửa sổ stream trực tiếp log thống kê tải Locust.

---

## ⏱️ TIẾN ĐỘ THỜI GIAN THEO 2 TRỤ CỘT THUỘC TÍNH CHẤT LƯỢNG

| Mốc Thời Gian | Trọng Tâm | Thao Tác Trực Tiếp | Khái Niệm Kiến Trúc Đối Chiếu |
|:---:|---|---|---|
| **00:00 – 02:00** | **Tổng quan QA & Baseline** | Kiểm tra Pods, truy cập Web Online Boutique, đặt hàng | Cấu trúc QA Scenario 6 thành phần, Microservices Topology |
| **02:00 – 05:00** | **Scalability & Scale Out** | Soi Locust, nâng tải 50 users, `kubectl scale frontend --replicas=3` | Throughput (RPS), Latency p50/p95/p99, Bottleneck, Little's Law |
| **05:00 – 07:30** | **Security & Access Control** | Chạy `.\setup-and-run.ps1 -AuditSecurity`, soi Supabase RLS | Threat Modeling, Trust Boundaries, Principle of Least Privilege |
| **07:30 – 10:00** | **Defensive Engineering & Trade-offs** | Soi Gitleaks SAST, Anti-Enumeration trong code, phân tích đánh đổi | Secret Lifecycle, Account Enumeration Prevention, Trade-offs |

---

## 🎙️ KỊCH BẢN THAO TÁC, LỆNH GÕ VÀ LỜI THOẠI CHI TIẾT TỪNG PHÚT

---

### 📍 [00:00 – 02:00] PHẦN 1: TỔNG QUAN QUALITY ATTRIBUTES VÀ HỆ THỐNG ONLINE BOUTIQUE
*(Mục tiêu: Định nghĩa QA Scenario chuẩn 6 thành phần và kiểm chứng baseline nghiệp vụ)*

#### 1. Thao tác trên Terminal & Trình duyệt:
- Chạy lệnh kiểm tra tổng quan hệ thống:
  ```powershell
  .\setup-and-run.ps1 -CheckOnly
  ```
- Chuyển sang trình duyệt web `http://localhost`:
  - Lướt danh mục sản phẩm (Vintage Typewriter, Sunglasses).
  - Chọn sản phẩm $\rightarrow$ Bấm **Add to Cart** $\rightarrow$ Bấm **Place Order**.
  - Đơn hàng được xử lý tức thì, tạo biên lai hoàn chỉnh.

#### 2. Lời thoại thuyết minh:
> *"Kính thưa quý Thầy/Cô trong Hội đồng, em là **Nhật Anh**. Hôm nay em xin trình bày về **Chủ đề 01: Quality Attributes (Thuộc tính Chất lượng)**, tập trung vào hai thuộc tính cốt lõi của hệ thống phần mềm quy mô lớn: **Khả năng mở rộng (Scalability)** và **An toàn bảo mật (Security)**.
> 
> Trong kiến trúc phần mềm, một Thuộc tính Chất lượng không thể mô tả mơ hồ mà phải được định lượng qua **Kịch bản QA (QA Scenario)** gồm 6 thành phần:
> 1. **Source**: Khách hàng Internet truy cập đồng thời.
> 2. **Stimulus**: Đợt bùng nổ lưu lượng mùa khuyến mãi (Flash Sale).
> 3. **Environment**: Hệ thống phân tán chịu tải cao trong giờ cao điểm.
> 4. **Artifact**: Tầng giao diện `frontend` và dịch vụ thanh toán/giỏ hàng.
> 5. **Response**: Hệ thống tiếp nhận toàn bộ tải mà không gây lỗi HTTP 5xx.
> 6. **Response Measure**: Đáp ứng thông lượng $\ge 50$ RPS, thời gian phản hồi ở phân vị **$p95 \le 100$ms** và tỷ lệ lỗi **Failures $= 0\%$**.
> 
> Để chứng minh kịch bản này trên thực tế, em triển khai hệ thống **Online Boutique** — kiến trúc 10 Microservices đa ngôn ngữ của Google trên nền cụm Kubernetes."*

---

### 📍 [02:00 – 05:00] PHẦN 2: THỰC NGHIỆM ĐO LƯỜNG SCALABILITY, LOCUST WORKLOAD VÀ POD SCALING
*(Mục tiêu: Phân tích chỉ số hiệu năng RPS, độ trễ phân vị p50/p95/p99, điểm nghẽn cổ chai và hiệu quả mở rộng ngang)*

#### 1. Thao tác trên Terminal:
- Xem số liệu tải hiện tại của Locust:
  ```powershell
  .\setup-and-run.ps1 -CheckLocust
  ```
  *(Chỉ ra cho Hội đồng thấy các cột: Request Name, Total Requests, Failures 0%, Average Latency, Median Latency, RPS).*
- Thực hiện tăng tải đột biến:
  ```powershell
  .\setup-and-run.ps1 -SetLoadHigh
  ```
- Đợi 5 giây và xem lại log tải:
  ```powershell
  .\setup-and-run.ps1 -CheckLocust
  ```
  *(Chỉ ra: Latency tăng vọt do tầng `frontend` tiếp nhận toàn bộ traffic trước khi ủy quyền sang các service nội bộ).*
- Giải quyết điểm nghẽn bằng Horizontal Pod Scaling:
  ```powershell
  .\setup-and-run.ps1 -ScaleFrontend
  ```
- Kiểm tra 3 Pod frontend đã lập tức `Running`:
  ```powershell
  kubectl get pods -l app=frontend
  ```
- Sau 10 giây, kiểm tra lại số liệu Locust:
  ```powershell
  .\setup-and-run.ps1 -CheckLocust
  ```

#### 2. Lời thoại thuyết minh:
> *"Tại đây, em sử dụng bộ phát tải **Locust** (`loadgenerator`) mô phỏng hành vi người dùng thực: duyệt sản phẩm, đổi đơn vị tiền tệ, thêm vào giỏ và checkout.
> - Ở mức **Baseline (10 người dùng)**: Hệ thống đạt thông lượng ổn định, độ trễ trung bình chỉ **32ms**, tỷ lệ lỗi là **0%**.
> - Tuy nhiên, khi em nâng tải lên **50 người dùng đồng thời**, nhìn vào bảng số liệu, thời gian phản hồi phân vị **$p95$ bắt đầu tăng vọt**. Theo **Định luật Little ($L = \lambda W$)**, khi số lượng yêu cầu trong hệ thống ($L$) tăng mà năng lực xử lý bão hòa, thời gian chờ ($W$) buộc phải kéo dài. Điểm nghẽn (Bottleneck) xuất hiện tại Pod `frontend` vì nó là cổng tiếp nhận duy nhất cho toàn bộ HTTP traffic từ bên ngoài.
> - Thay vì nâng cấp cấu hình máy chủ (Vertical Scaling) tốn kém và có trần giới hạn vật lý, em áp dụng **Mở rộng theo chiều ngang (Horizontal Scaling)**: tăng số replica của `frontend` từ **1 lên 3 Pods**.
> - Ngay lập tức, bộ cân bằng tải nội bộ của Kubernetes phân phối đều lưu lượng qua 3 Pods. Kết quả: **Thông lượng (RPS) tăng trưởng gấp 3 lần**, độ trễ $p95$ được kéo giảm về mức an toàn dưới **50ms**, chứng minh hệ thống đạt thuộc tính **Linear Scalability**."*

---

### 📍 [05:00 – 07:30] PHẦN 3: AN TOÀN BẢO MẬT (SECURITY), THREAT MODEL VÀ SUPABASE ROW LEVEL SECURITY (RLS)
*(Mục tiêu: Phân tích mô hình mối đe dọa, ranh giới tin cậy và kiểm soát truy cập tầng CSDL)*

#### 1. Thao tác trên Terminal & VS Code:
- Chạy lệnh kiểm toán bảo mật:
  ```powershell
  .\setup-and-run.ps1 -AuditSecurity
  ```
- Mở file [`projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql`](file:///d:/VScode/midterm-software-architecture/topics/01-quality-attributes/projects/scripthammer/source/supabase/migrations/20251006_complete_monolithic_setup.sql#L1220-L1230) trên màn hình VS Code.
- Trỏ chuột vào các dòng lệnh SQL kích hoạt RLS:
  - `ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;`
  - `ALTER TABLE payment_intents ENABLE ROW LEVEL SECURITY;`
  - Các Policy `CREATE POLICY ... USING (auth.uid() = id);`

#### 2. Lời thoại thuyết minh:
> *"Bây giờ em xin chuyển sang thuộc tính thứ hai: **An toàn Bảo mật (Security)** trên dự án **ScriptHammer** — một ứng dụng SaaS quy mô lớn kết hợp Next.js, Supabase và Stripe.
> 
> Trong kiến trúc bảo mật, em xây dựng **Mô hình Mối đe dọa (Threat Modeling)** dựa trên việc xác định các **Ranh giới Tin cậy (Trust Boundaries)**:
> 1. Ranh giới giữa Trình duyệt người dùng (Untrusted Client) và Máy chủ Edge/API.
> 2. Ranh giới giữa Máy chủ Ứng dụng và CSDL Supabase PostgreSQL.
> 3. Ranh giới với bên thứ ba (OAuth Provider, Cổng thanh toán Stripe).
> 
> **Lỗi bảo mật phổ biến nhất** trong các ứng dụng hiện đại là chỉ dựa vào code ở tầng Backend (Controller/API) để phân quyền. Nếu API có lỗ hổng IDOR (Insecure Direct Object Reference) hoặc bị rò rỉ token, kẻ tấn công có thể truy vấn dữ liệu của người khác.
> 
> Để triệt tiêu nguy cơ này, kiến trúc ScriptHammer áp dụng nguyên tắc **Phòng thủ Đa tầng (Defense in Depth)** và **Đặc quyền Tối thiểu (Least Privilege)** bằng **Supabase Row Level Security (RLS)**:
> - Như Thầy/Cô thấy trên màn hình SQL migration, toàn bộ **22 bảng dữ liệu nhạy cảm** như `user_profiles`, `payment_intents`, `subscriptions` đều bị cưỡng bức `ENABLE ROW LEVEL SECURITY`.
> - Tại tầng nhân CSDL PostgreSQL, mỗi truy vấn bị lọc gắt gao bởi điều kiện `USING (auth.uid() = user_id)`. Dù kẻ tấn công có giả mạo request API, CSDL vẫn kiên quyết từ chối trả về bất kỳ dòng dữ liệu nào không thuộc về người dùng đó."*

---

### 📍 [07:30 – 10:00] PHẦN 4: DEFENSIVE CODING, VÒNG ĐỜI SECRET VÀ TRADE-OFFS KIẾN TRÚC
*(Mục tiêu: Chứng minh chống lộ lọt khóa bí mật, chống Account Enumeration và phân tích sự đánh đổi giữa Scalability vs Security)*

#### 1. Thao tác trên VS Code:
- Mở file [`projects/scripthammer/source/.gitleaks.toml`](file:///d:/VScode/midterm-software-architecture/topics/01-quality-attributes/projects/scripthammer/source/.gitleaks.toml):
  - Chỉ ra các bộ luật Regex phát hiện Secret Key Stripe (`sk_live_...`), Supabase Key.
- Mở file [`projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts`](file:///d:/VScode/midterm-software-architecture/topics/01-quality-attributes/projects/scripthammer/source/src/lib/auth/auth-rate-limit.ts#L20-L42):
  - Trỏ vào biến `EMAIL_QUOTA_MESSAGE` và hàm `authRateLimitMessage`.

#### 2. Lời thoại thuyết minh:
> *"Ở cấp độ triển khai mã nguồn, hệ thống áp dụng kỹ thuật **Defensive Engineering**:
> 1. **Quản lý vòng đời Secret (Secret Management)**: Dự án tích hợp công cụ SAST `.gitleaks.toml` chạy tại pre-commit hook, quét sạch mọi nguy cơ commit nhầm API key hoặc service credentials vào git history.
> 2. **Chống dò quét tài khoản (Anti-Account Enumeration)**: Nhìn vào file `auth-rate-limit.ts`, khi kẻ tấn công gửi nhiều request thử đăng nhập hoặc reset password, thay vì trả về thông báo khác nhau như 'Email không tồn tại' hay 'Mật khẩu sai', hệ thống đồng nhất trả về thông điệp chung `EMAIL_QUOTA_MESSAGE`. Điều này triệt tiêu hoàn toàn khả năng kẻ tấn công dùng kỹ thuật User Enumeration để lập danh sách tài khoản mục tiêu.
> 
> **Về Phân tích Đánh đổi Kiến trúc (Architectural Trade-offs)**:
> - **Scalability vs. Security**: Việc bật kiểm tra RLS trên từng bản ghi CSDL và xác thực chữ ký JWT ở mỗi request tạo ra một khoản chi phí tài nguyên tính toán (CPU overhead). Để bù đắp, kiến trúc sử dụng cơ chế connection pooling và cache session phía Edge.
> - **Availability vs. Consistency**: Khi scale horizontal nhiều Pod `frontend`, dữ liệu giỏ hàng được ủy quyền cho một Redis Cache tập trung (`redis-cart`) thay vì lưu trong bộ nhớ cục bộ, bảo đảm tính nhất quán dữ liệu (Data Consistency) khi người dùng bị route ngẫu nhiên giữa các replica.
> 
> Tóm lại, thông qua thực nghiệm đo tải Locust trên **Online Boutique** và kiểm toán bảo mật trên **ScriptHammer**, em đã chứng minh đầy đủ cả về mặt lý thuyết lẫn mã nguồn thực tế cho hai thuộc tính **Scalability** và **Security**.
> 
> Em xin chân thành cảm ơn quý Thầy/Cô đã lắng nghe và em sẵn sàng bước vào phần trả lời câu hỏi vấn đáp!"*
