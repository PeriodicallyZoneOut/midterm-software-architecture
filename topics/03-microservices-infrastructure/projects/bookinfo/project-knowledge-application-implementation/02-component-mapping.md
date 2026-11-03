# Bảng ánh xạ thành phần (Component Mapping) — Bookinfo

Tài liệu này chi tiết hóa mối liên kết giữa kiến trúc logic, mã nguồn, cấu hình Docker container, tài nguyên Kubernetes và hạ tầng Istio Service Mesh của toàn bộ 4 microservices trong Bookinfo.

---

## 1. Sơ đồ Tô-pô Tương tác giữa các Thành phần

```mermaid
flowchart TD
    subgraph Ingress ["1. Ingress Layer"]
        User(["Client Browser"]) -->|HTTP Port 80| Gateway["Istio Ingress Gateway<br/>(Envoy Proxy)"]
    end

    subgraph Mesh ["2. Bookinfo Mesh (default namespace with Envoy sidecars)"]
        Gateway -->|HTTP /productpage| PP["productpage-v1<br/>(Python/Flask :9080)<br/>+ istio-proxy"]
        
        PP -->|GET /details/0| Det["details-v1<br/>(Ruby/WEBrick :9080)<br/>+ istio-proxy"]
        PP -->|GET /reviews/0<br/>Header: end-user| RevRouter{"Istio VirtualService<br/>(reviews L7 Router)"}
        
        RevRouter -->|Default: 100%| Rev1["reviews-v1<br/>(Java Liberty :9080)<br/>No ratings"]
        RevRouter -->|User: jason| Rev2["reviews-v2<br/>(Java Liberty :9080)<br/>Black stars"]
        RevRouter -->|Canary: 50%| Rev3["reviews-v3<br/>(Java Liberty :9080)<br/>Red stars"]
        
        Rev2 -->|GET /ratings/0| Rat["ratings-v1<br/>(Node.js Express :9080)<br/>+ istio-proxy"]
        Rev3 -->|GET /ratings/0| Rat
    end

    subgraph Observability ["3. Observability Plane (istio-system)"]
        Prom["Prometheus Server<br/>(:9090)"] -.->|Scrape :15090/stats/prometheus| PP
        Prom -.->|Scrape :15090/stats/prometheus| Det
        Prom -.->|Scrape :15090/stats/prometheus| Rev1
        Prom -.->|Scrape :15090/stats/prometheus| Rev2
        Prom -.->|Scrape :15090/stats/prometheus| Rev3
        Prom -.->|Scrape :15090/stats/prometheus| Rat
        Grafana["Grafana Dashboards<br/>(:3000)"] -->|Query PromQL| Prom
    end

    classDef k8s fill:#e1f5fe,stroke:#0288d1,stroke-width:1px;
    classDef istio fill:#ede7f6,stroke:#512da8,stroke-width:1px;
    classDef obs fill:#fff3e0,stroke:#f57c00,stroke-width:1px;
    class PP,Det,Rev1,Rev2,Rev3,Rat k8s;
    class Gateway,RevRouter istio;
    class Prom,Grafana obs;
```

---

## 2. Bảng Ánh xạ Toàn bộ Thành phần (Component Mapping Table)

| Tên Microservice | Ngôn ngữ / Framework | Vị trí Source Code | Container Port / Service Port | Tài nguyên Kubernetes | Nhãn (Labels) | Phụ thuộc Downstream | Vai trò trong Hệ thống |
|---|---|---|---|---|---|---|---|
| **`productpage`** | Python 3.7+ / Flask, OpenTelemetry, Prometheus Client | `src/productpage/productpage.py` | `9080` / `9080` (ClusterIP) | Deployment `productpage-v1`, Service `productpage`, SA `bookinfo-productpage` | `app: productpage`, `version: v1` | `details:9080`, `reviews:9080` | Frontend UI / API Gateway Aggregator hiển thị thông tin sách và bài đánh giá |
| **`details`** | Ruby 2.7+ / WEBrick & Sinatra | `src/details/details.rb` | `9080` / `9080` (ClusterIP) | Deployment `details-v1`, Service `details`, SA `bookinfo-details` | `app: details`, `version: v1` | Không | Cung cấp thông tin metadata xuất bản của sách (thể loại, trang, NXB, ISBN) |
| **`reviews` (v1)** | Java 8+ / Open Liberty, JAX-RS | `src/reviews/reviews-application/` | `9080` / `9080` (ClusterIP) | Deployment `reviews-v1`, Service `reviews`, SA `bookinfo-reviews` | `app: reviews`, `version: v1` | Không (Ratings disabled) | Phiên bản baseline phục vụ bình luận sách dạng text thuần túy, không có sao đánh giá |
| **`reviews` (v2)** | Java 8+ / Open Liberty, JAX-RS | `src/reviews/reviews-application/` | `9080` / `9080` (ClusterIP) | Deployment `reviews-v2`, Service `reviews`, SA `bookinfo-reviews` | `app: reviews`, `version: v2` | `ratings:9080` | Phiên bản mở rộng gọi sang `ratings` và hiển thị sao màu đen (`STAR_COLOR=black`) |
| **`reviews` (v3)** | Java 8+ / Open Liberty, JAX-RS | `src/reviews/reviews-application/` | `9080` / `9080` (ClusterIP) | Deployment `reviews-v3`, Service `reviews`, SA `bookinfo-reviews` | `app: reviews`, `version: v3` | `ratings:9080` | Phiên bản canary nâng cao gọi sang `ratings` và hiển thị sao màu đỏ (`STAR_COLOR=red`) |
| **`ratings`** | Node.js 12+ / Express, httpdispatcher | `src/ratings/ratings.js` | `9080` / `9080` (ClusterIP) | Deployment `ratings-v1`, Service `ratings`, SA `bookinfo-ratings` | `app: ratings`, `version: v1` | Có thể nối MySQL/MongoDB | Cung cấp điểm số đánh giá từ 1 đến 5 sao theo từng reviewer |

---

## 3. Ánh xạ Hạ tầng Istio Service Mesh & Observability

| Thành phần Hạ tầng | Loại tài nguyên (Kind) | Vị trí file cấu hình | Port kết nối | Trách nhiệm và Chức năng |
|---|---|---|---|---|
| **Istio Ingress Gateway** | `Gateway` (`networking.istio.io/v1alpha3`) | `networking/bookinfo-gateway.yaml` | `80` (HTTP) / `443` (HTTPS) | Điểm tiếp nhận traffic từ ngoài Internet/Host vào cụm, mở cổng tiếp nhận cho host `*` |
| **Productpage VirtualService** | `VirtualService` (`networking.istio.io/v1alpha3`) | `networking/bookinfo-gateway.yaml` | `9080` | Định tuyến các URI `/productpage`, `/static`, `/login`, `/logout` từ Ingress Gateway vào Service `productpage` |
| **Destination Rules (All)** | `DestinationRule` (`networking.istio.io/v1alpha3`) | `networking/destination-rule-all.yaml` | N/A | Định nghĩa danh sách các Subsets dựa theo nhãn Kubernetes (`version: v1`, `version: v2`, `version: v3`) cho cả 4 services |
| **Canary Header VirtualService** | `VirtualService` (`networking.istio.io/v1alpha3`) | `networking/virtual-service-reviews-test-v2.yaml` | `9080` | Bắt header `end-user: jason` để route vào `reviews:v2`, các user khác vào `reviews:v1` |
| **Traffic Shifting VirtualService** | `VirtualService` (`networking.istio.io/v1alpha3`) | `networking/virtual-service-reviews-50-v3.yaml` | `9080` | Phân bổ tỉ lệ tải 50% vào `reviews:v1` và 50% vào `reviews:v3` |
| **Fault Injection VirtualService** | `VirtualService` (`networking.istio.io/v1alpha3`) | `networking/virtual-service-ratings-test-delay.yaml` | `9080` | Giả lập độ trễ cố định 7 giây (HTTP Delay) 100% request từ user `jason` khi gọi service `ratings` |
| **Envoy Sidecar (`istio-proxy`)** | Container nội bộ Pod | Tự động tiêm bởi Istiod qua Webhook | `15090` (Prometheus), `15021` (Health), `15001` (Outbound), `15006` (Inbound) | Chặn và xử lý toàn bộ traffic L4/L7, thực thi mTLS, thu thập metrics telemetry |
| **Prometheus Server** | Deployment / Service K8s | `../../istio/source/samples/addons/prometheus.yaml` | `9090` | Thu thập (scrape) định kỳ các metrics tiêu chuẩn từ cổng `:15090/stats/prometheus` của từng Envoy sidecar |
| **Grafana Dashboard** | Deployment / Service K8s | `../../istio/source/samples/addons/grafana.yaml` | `3000` | Trực quan hóa dữ liệu qua các dashboard chuyên dụng: Istio Mesh Dashboard, Istio Service Dashboard, Istio Workload Dashboard |

