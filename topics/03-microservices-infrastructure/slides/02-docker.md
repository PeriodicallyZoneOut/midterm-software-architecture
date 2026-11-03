---
marp: true
theme: default
paginate: true
header: 'Chủ đề 3.2: Đóng gói Container với Docker | Tường'
footer: 'Kiến trúc Phần mềm — Báo cáo Giữa kỳ'
style: |
  section { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 35px; }
  h1 { color: #58a6ff; font-size: 26px; }
  h2, h3 { color: #79c0ff; font-size: 20px; }
  table { font-size: 13px; color: #c9d1d9; width: 100%; }
  th { background-color: #161b22; color: #58a6ff; }
  code { background-color: #161b22; color: #ff7b72; font-size: 12px; }
  pre { background-color: #161b22; font-size: 11px; padding: 10px; }
---

# SLIDE 1: ĐẶT VẤN ĐỀ & SỰ RA ĐỜI CỦA CONTAINERIZATION
- **Học phần**: Kiến trúc Phần mềm — Báo cáo Chuyên sâu: **Docker & Containerization**
- **Người thực hiện**: Tường (Thời lượng: 10 phút)
- **Hệ thống minh chứng**: [Bookinfo Dockerfiles](../../projects/bookinfo/source/src)

### Vấn Đề Lịch Sử "It Works on My Machine":
- Ứng dụng chạy tốt trên máy lập trình viên nhưng lỗi thư viện/OS khi deploy lên server staging/production.
- Máy ảo truyền thống (Virtual Machines) quá nặng: mỗi VM chứa một bản sao OS đầy đủ (Guest OS), tiêu tốn hàng GB RAM và khởi động mất vài phút.
- **Giải pháp Docker**: Đóng gói mã nguồn cùng toàn bộ dependencies thành một đơn vị thực thi chuẩn hóa, chia sẻ trực tiếp Host OS Kernel.

---

# SLIDE 2: SO SÁNH CONTAINER VS VIRTUAL MACHINE (VM)

| Tiêu chí | Virtual Machine (VM) | Docker Container |
|---|---|---|
| **Cơ chế Ảo hóa** | Ảo hóa phần cứng qua Hypervisor (Type 1/Type 2) | Ảo hóa mức hệ điều hành (OS-level virtualization) |
| **Hệ Điều Hành** | Mỗi VM mang 1 Guest OS riêng biệt | Chia sẻ chung **Host Linux Kernel** |
| **Kích thước Image** | Rất lớn (vài GB đến hàng chục GB) | Nhỏ gọn (vài chục MB đến vài trăm MB) |
| **Thời gian Khởi động** | Vài phút (chờ nạp boot OS) | **Mili-giây** (chỉ khởi chạy tiến trình con) |
| **Tiêu tốn Tài nguyên** | Cố định tài nguyên (RAM/CPU cấp trước) | Cấp phát linh hoạt theo tải thực tế |
| **Mức độ Cách ly** | Cách ly phần cứng tuyệt đối | Cách ly tiến trình qua Kernel primitives |

---

# SLIDE 3: LINUX KERNEL PRIMITIVES — NỀN TẢNG CỐT LÕI CỦA DOCKER
*Docker không tự tạo ra sự cách ly; Docker sử dụng các tính năng sẵn có của Linux Kernel*

### 1. Linux Namespaces (Cung cấp ranh giới Cách ly):
- **PID Namespace**: Cách ly cây tiến trình; tiến trình trong container thấy mình là PID 1.
- **NET Namespace**: Cung cấp card mạng ảo riêng (`eth0`), bảng định tuyến và loopback riêng.
- **MNT Namespace**: Cách ly hệ thống file mount point.
- **IPC Namespace**: Cách ly bộ nhớ chia sẻ (Shared memory).
- **UTS Namespace**: Cách ly hostname và domain name.

### 2. Linux Cgroups (Control Groups — Kiểm soát Tài nguyên):
- Áp đặt giới hạn trần tài nguyên: CPU quotas, Memory limits, I/O bandwidth.
- Ngăn chặn một container bị lỗi rò rỉ bộ nhớ làm cạn kiệt tài nguyên toàn bộ máy chủ vật lý.

---

# SLIDE 4: KIẾN TRÚC DOCKER ENGINE & OCI STANDARDS
*Từ dòng lệnh `docker run` đến container thực thi*

### Luồng Kiến Trúc Docker Engine:
```text
[ Docker CLI ] ──REST API──> [ dockerd (Daemon) ]
                                    │
                                    ▼
                             [ containerd ] ──gRPC──> [ runc (OCI Runtime) ]
                                                            │
                                                            ▼
                                                   [ Container Process ]
```
- **dockerd**: Quản lý image, volume, network và API server.
- **containerd**: Bộ quản lý vòng đời container chuẩn công nghiệp (CNCF graduated).
- **runc**: Hiện thực hóa chuẩn Open Container Initiative (OCI), trực tiếp giao tiếp với Linux Kernel để cấu hình namespaces và cgroups.

---

# SLIDE 5: DOCKERFILE INSTRUCTIONS & CƠ CHẾ CACHING IMAGE LAYER
*Hiểu sâu về cấu trúc tầng và tối ưu hóa thời gian build*

### Nguyên Lý Union File System (UnionFS):
- Mỗi chỉ thị trong Dockerfile (`FROM`, `RUN`, `COPY`) tạo ra một Layer **Read-Only**.
- Khi container chạy, Docker phủ một tầng **Read-Write Thin Layer** lên trên cùng.

### Chiến Thuật Tối Ưu Hóa Thứ Tự Lệnh:
```dockerfile
# 1. Copy file định nghĩa thư viện TRƯỚC (Ít thay đổi) -> Tận dụng Build Cache
COPY requirements.txt .
RUN pip install -r requirements.txt

# 2. Copy mã nguồn SAU (Thay đổi thường xuyên)
COPY . .
```
- Nếu chỉ sửa code, Docker bỏ qua lệnh cài thư viện nặng, giảm thời gian build từ 5 phút xuống còn **2 giây**!

---

# SLIDE 6: CODE DEEP-DIVE: DOCKER MULTI-STAGE BUILD TRONG BOOKINFO
*Phân tích file `src/reviews/Dockerfile`*

```dockerfile
# ==============================================================================
# STAGE 1: Compilation Environment (Chứa Gradle compiler + JDK 8)
# ==============================================================================
FROM gradle:4.8.1-jdk8-alpine as builder
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src/reviews-wlpcfg
RUN gradle build

# ==============================================================================
# STAGE 2: Minimal Production Runtime Image
# ==============================================================================
FROM open-liberty:kernel-slim
COPY --chown=1001:0 --from=builder \
     /home/gradle/src/reviews-wlpcfg/build/libs/wlp/usr/servers/defaultServer \
     /opt/ibm/wlp/usr/servers/defaultServer
EXPOSE 9080
```
- **Kết quả đo đạc**: Image rút gọn từ **>800MB** xuống còn **~150MB**.
- **Bảo mật**: Loại bỏ hoàn toàn Gradle compiler, JDK và source code thô khỏi production image.

---

# SLIDE 7: DOCKER NETWORKING & SERVICE EXPOSURE
*Cách thức các container giao tiếp với nhau và với thế giới bên ngoài*

### 4 Chế Độ Mạng Cơ Bản trong Docker:
1. **Bridge (Mặc định)**: Tạo cầu nối mạng ảo `docker0`, cấp dải IP riêng (172.17.x.x) cho từng container.
2. **Host**: Container dùng chung card mạng và port trực tiếp với Host OS (hiệu năng cao nhất, không cách ly port).
3. **Overlay**: Cho phép các container trên nhiều máy chủ vật lý khác nhau nói chuyện qua mạng VXLAN (nền tảng của Swarm/K8s).
4. **None**: Tắt hoàn toàn mạng, dùng cho các batch job cần bảo mật tối đa.

### Cơ Chế Port Mapping (`-p 9080:9080`):
- Docker daemon tạo các luật `iptables` NAT để chuyển tiếp (forward) traffic từ cổng host vào card mạng ảo của container.

---

# SLIDE 8: DOCKER STORAGE — VOLUMES VS BIND MOUNTS
*Quản lý dữ liệu bền vững (Persistence) cho Microservices*

### So Sánh 3 Cơ Chế Lưu Trữ:
- **Volumes**: Được Docker quản lý tập trung tại `/var/lib/docker/volumes/`. An toàn, dễ backup, hiệu năng cao, khuyến nghị cho Database (MySQL/Ratings).
- **Bind Mounts**: Gắn trực tiếp một thư mục cụ thể từ máy host vào container. Tiện lợi khi phát triển phần mềm (live reload code).
- **tmpfs Mounts**: Ghi dữ liệu trực tiếp vào RAM của host, không ghi xuống đĩa, dùng cho dữ liệu nhạy cảm hoặc cache tạm thời.

```text
Host Filesystem ──Bind Mount──> [ /app/source ] in Container
Docker Volume Area ──Named Vol──> [ /var/lib/mysql ] in Container
Host Memory (RAM) ──tmpfs Mount──> [ /tmp ] in Container
```

---

# SLIDE 9: BẢO MẬT CONTAINER (CONTAINER SECURITY HARDENING)
*Các nguyên tắc bảo mật tối thượng khi đóng gói Docker*

### 4 Nguyên Tắc Vàng cho Production Image:
1. **Chạy dưới User Non-Root**:
   - Mặc định container chạy bằng `root`. Nếu bị khai thác lỗ hổng Remote Code Execution, kẻ tấn công chiếm quyền host.
   - Luôn định nghĩa: `USER 1001` (như trong `src/reviews/Dockerfile`).
2. **Sử dụng Base Image Tối Giản**:
   - Ưu tiên `alpine` hoặc `distroless` (không chứa shell `/bin/sh` hay package manager `apt/yum`).
3. **Read-Only Root Filesystem**:
   - Chạy container với cờ `--read-only`, ngăn ngừa mã độc ghi file thực thi vào hệ thống.
4. **Quét Lỗ Hổng Bảo Mật (Vulnerability Scanning)**:
   - Tích hợp `docker scan` hoặc Trivy vào CI/CD pipeline để phát hiện CVE trong thư viện bên thứ ba.

---

# SLIDE 10: TỔNG KẾT & ARCHITECTURAL TRADE-OFFS CỦA DOCKER

### Bảng Đánh Đổi Kiến Trúc (Trade-offs):

| Lợi Thế Đạt Được | Chi Phí & Thách Thức Vận Hành | Giải Pháp Khắc Phục |
|---|---|---|
| **Portability Tuyệt Đối**: Chạy nhất quán 100% trên mọi môi trường. | **Layer Sprawl**: Image phình to nếu viết Dockerfile kém. | Áp dụng Multi-stage build và `.dockerignore`. |
| **Mật Độ Cao (High Density)**: Chạy hàng chục container trên 1 host. | **Shared Kernel Risk**: Lỗ hổng kernel có thể vượt rào cách ly (Container breakout). | Cập nhật kernel thường xuyên, chạy non-root, bật seccomp/AppArmor. |
| **Khởi Động Nhanh**: Tính bằng mili-giây, scale cực nhanh. | **State Persistence**: Khó quản lý stateful data qua nhiều node. | Tách rời state ra Storage Volume hoặc Database-as-a-Service. |

---

## 🎙️ KỊCH BẢN THUYẾT TRÌNH 10 PHÚT — CHỦ ĐỀ DOCKER

- **[0:00 – 1:00] Slide 1 & 2**: *"Kính thưa Thầy/Cô, em là Tường, trình bày về Công nghệ Đóng gói Docker. Docker giải quyết vấn đề 'chạy được ở máy tôi nhưng lỗi ở production' bằng cách ảo hóa mức hệ điều hành, chia sẻ chung Linux Kernel, giúp khởi động tính bằng mili-giây và kích thước nhỏ hơn máy ảo VM hàng chục lần."*
- **[1:00 – 2:30] Slide 3 & 4**: *"Nền tảng của Docker dựa trên hai primitive của Linux Kernel: Namespaces để cách ly tiến trình (PID), card mạng (NET), file system (MNT); và Cgroups để áp đặt giới hạn CPU/RAM. Kiến trúc Docker Engine đi từ CLI sang daemon, qua containerd và runc theo chuẩn OCI để tạo container."*
- **[2:30 – 4:00] Slide 5 & 6**: *(Mở file `src/reviews/Dockerfile`)*: *"Image Docker được cấu tạo từ các Layer chỉ đọc. Để tối ưu hóa, em áp dụng kỹ thuật Multi-stage build cho dịch vụ Java `reviews`: Stage 1 dùng Gradle trên Alpine để build code; Stage 2 chỉ copy file `.war` sang runtime Open Liberty kernel-slim. Dung lượng giảm từ >800MB xuống 150MB, đồng thời loại bỏ compiler khỏi production image."*
- **[4:00 – 5:30] Slide 7 & 8**: *"Về mạng, Docker cung cấp Bridge, Host, Overlay và cơ chế port mapping qua iptables. Về dữ liệu, Docker hỗ trợ Volume độc lập để đảm bảo dữ liệu không bị mất khi container bị hủy."*
- **[5:30 – 6:30] Slide 9 & 10**: *"Về bảo mật, em tuân thủ chạy non-root user (USER 1001), dùng base image tối giản để thu hẹp bề mặt tấn công. Đánh đổi lớn nhất của Docker là rủi ro chia sẻ chung kernel, nhưng được kiểm soát tốt bằng cgroups và seccomp."*
- **[6:30 – 9:30] Live Demo**: Chạy lệnh kiểm tra image `docker images`, so sánh kích thước builder vs final, inspect namespaces của container đang chạy.
- **[9:30 – 10:00] Kết bài & Vấn đáp**: Tuyên bố kết thúc bài thuyết trình Docker.

