---
marp: true
theme: default
paginate: true
header: 'Microservices & Cloud-Native Infrastructure | Topic 03'
footer: 'Presenter: Tuong | Midterm Software Architecture'
style: |
  section {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #0d1117;
    color: #c9d1d9;
    padding: 35px;
  }
  h1 {
    color: #58a6ff;
    font-size: 26px;
  }
  h2, h3 {
    color: #79c0ff;
    font-size: 20px;
  }
  table {
    font-size: 13px;
    color: #c9d1d9;
    width: 100%;
  }
  th {
    background-color: #161b22;
    color: #58a6ff;
  }
  code {
    background-color: #161b22;
    color: #ff7b72;
    font-size: 12px;
  }
  pre {
    background-color: #161b22;
    font-size: 11px;
    padding: 10px;
  }
---

<!-- 
AI SLIDE GENERATOR PROMPT (For Gamma.app, Tome, or ChatGPT/Claude PPTX generator):

You are a Senior Software Architect and Cloud-Native SRE Specialist.
Please generate an executive 10-slide presentation deck based on the structured markdown content below.
Technologies covered: Microservices, Docker, Kubernetes, Istio, Prometheus, Grafana, Bookinfo.
Theme: Cloud-Native & Enterprise Tech (Dark theme, Navy Blue #0A192F, Cyan Accent #00E5FF, White text).
Layout: Clean 2-column or 3-column layouts, comparison tables, code blocks, and architecture diagrams.
-->

# Slide 1: Title & The Cloud-Native Infrastructure Paradigm

## MICROSERVICES & CLOUD-NATIVE INFRASTRUCTURE
### Design, Deployment, Orchestration & Observability with Docker, Kubernetes, Istio, Prometheus & Grafana

- **Course**: Software Architecture — Midterm Defense
- **Presenter**: Tuong
- **Demonstration System**: Bookinfo (Canonical Istio Polyglot Microservices Sample)

### 4 Core Infrastructure Challenges in Distributed Systems:
1. **Inter-Service Networking**: How to dynamically route heterogeneous traffic and execute Canary releases?
2. **Container Orchestration**: How to guarantee self-healing and zero-downtime rolling updates automatically?
3. **Internal Network Security**: How to enforce Zero Trust security and encrypt inter-pod traffic with zero code changes?
4. **Distributed Observability**: How to centrally aggregate telemetry and trace bottlenecks across multi-hop calls?

---

# Slide 2: Architectural Comparison & Polyglot Bookinfo

### 1. Architectural Paradigm Comparison Matrix:

| Evaluation Dimension | Monolith | Modular Monolith | Microservices (Bookinfo) |
|---|---|---|---|
| **Runtime Structure** | Single process hosting all logic | Single process, strictly partitioned modules | Each service is an isolated process (Container) |
| **Data Ownership** | Shared central database | Single DB with module-specific schemas | **Database-per-service** autonomy |
| **Technology Stack** | Homogeneous language/framework | Homogeneous language | **Polyglot**: Optimal stack per business domain |
| **Blast Radius** | Critical: A bug in one module crashes all | High: Runtime failure halts entire process | **Isolated**: Failures contained within service bounds |
| **Scalability** | Coarse-grained (scales entire application) | Coarse-grained (scales entire binary) | **Fine-grained**: Scale individual bottlenecks |
| **Operational Overhead** | Low (Single deployment unit) | Moderate | **High** (Demands K8s, Mesh, Observability) |

### 2. Polyglot Microservices in Bookinfo:
- **Python (Flask)**: `productpage` — High-velocity Jinja2 web rendering & API aggregation.
- **Ruby (WEBrick/Sinatra)**: `details` — Lightweight book metadata retrieval.
- **Java (Open Liberty)**: `reviews` — Enterprise-grade concurrency, hosting v1, v2, and v3.
- **Node.js (Express)**: `ratings` — Non-blocking, event-driven I/O for score lookups.

---

# Slide 3: Domain Decomposition (DDD) & Code Mapping in Bookinfo

### 1. Bounded Contexts & Single Responsibility Principle (DDD):
- **`productpage`**: Presentation tier and API aggregator. Assembles book details and reviews into HTML.
- **`details`**: Manages book publishing metadata (category, pages, publisher, language, ISBN).
- **`reviews`**: Manages user book reviews across three distinct release versions:
  - *v1*: Pure text reviews (does not call the ratings service).
  - *v2*: Calls `ratings` service; displays 1 to 5 **black stars** (`STAR_COLOR=black`).
  - *v3*: Calls `ratings` service; displays 1 to 5 **red stars** (`STAR_COLOR=red`).
- **`ratings`**: Encapsulates scoring computations (1–5 stars) with optional MySQL/MongoDB persistence.

### 2. Code Mapping in Java Reviews (`LibertyRestEndpoint.java`):
```java
private final static Boolean ratings_enabled = Boolean.valueOf(System.getenv("ENABLE_RATINGS"));
private final static String star_color = System.getenv("STAR_COLOR") == null ? "black" : System.getenv("STAR_COLOR");
```
*12-Factor App Methodology: A single unified Java codebase where v1, v2, and v3 behaviors are controlled dynamically via environment variables.*

---

# Slide 4: Inter-Service Communication & Tracing Header Propagation

### 1. The Distributed Tracing Challenge:
- Requests traverse: `Browser` ➔ `productpage` ➔ `reviews` ➔ `ratings`.
- Without Context Propagation, distributed traces break, and the Envoy proxy loses Layer 7 user routing capabilities.

### 2. Code Deep-Dive: Header Forwarding in `productpage.py`:
```python
def getForwardHeaders(request):
    headers = {}
    # 1. Extract and inject B3 tracing context via OpenTelemetry
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)

    # 2. Forward user identity context for Layer 7 Canary Routing
    if 'user' in session:
        headers['end-user'] = session['user']

    # 3. Propagate standard Istio/Envoy tracing headers
    for hdr in ['x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-sampled']:
        if hdr in request.headers:
            headers[hdr] = request.headers[hdr]
    return headers
```
- **Canary Prerequisite**: Propagating `end-user: jason` enables the Envoy proxy to inspect headers at Layer 7 and route user `jason` to `reviews:v2`.

---

# Slide 5: Containerization & Docker Multi-Stage Build

### 1. Linux Kernel Primitives for Container Isolation:
- **Linux Namespaces**: Provides execution boundary isolation (`PID` process tree, `NET` network stack, `MNT` mount points).
- **Linux Cgroups (Control Groups)**: Enforces hard resource ceilings (`CPU limits`, `Memory limits`), preventing host starvation.

### 2. Multi-Stage Build Analysis in `src/reviews/Dockerfile`:
```dockerfile
# STAGE 1: Compilation Environment (Full Gradle + OpenJDK 8 Alpine)
FROM gradle:4.8.1-jdk8-alpine as builder
COPY --chown=gradle:gradle . /home/gradle/src
WORKDIR /home/gradle/src/reviews-wlpcfg
RUN gradle build

# STAGE 2: Minimal Production Runtime Image
FROM open-liberty:kernel-slim
COPY --chown=1001:0 --from=builder \
     /home/gradle/src/reviews-wlpcfg/build/libs/wlp/usr/servers/defaultServer \
     /opt/ibm/wlp/usr/servers/defaultServer
EXPOSE 9080
```
- **Efficiency**: Shrinks container size from **>800MB** down to **~150MB**.
- **Security Hardening**: Completely purges Gradle build tools, compilers, and source code from the final runtime ➔ **Minimizes Attack Surface**.

---

# Slide 6: Kubernetes Workload Modeling & Label Selectors

### 1. Dual-Container Pod Architecture (`2/2 Running`):
- Container 1: **Application Business Logic** (`productpage`, `details`, `reviews`, `ratings`).
- Container 2: **Envoy Sidecar Proxy (`istio-proxy`)** injected automatically via Mutating Admission Webhook.

### 2. Multi-Version Deployment Topography via Label Selectors:
```text
ClusterIP Service: reviews (Port: 9080, Selector: app=reviews)
   ├── Deployment: reviews-v1 (Labels: app=reviews, version=v1) ──▶ Plain Text
   ├── Deployment: reviews-v2 (Labels: app=reviews, version=v2) ──▶ Black Stars
   └── Deployment: reviews-v3 (Labels: app=reviews, version=v3) ──▶ Red Stars
```
- **Default L4 Round-Robin**: Without Istio, Kubernetes Service distributes requests across all Pods matching `app: reviews` evenly (~33% per version).
- **ClusterIP Abstraction**: Exposes a stable internal DNS endpoint (`http://reviews:9080`) decoupled from ephemeral Pod IP addresses.

---

# Slide 7: Kubernetes Self-Healing & Zero-Downtime Deployment

### 1. Self-Healing via Continuous State Reconciliation:
- Kubernetes operates on an active control loop:
  $$\text{Current State} \xrightarrow{\quad\text{Reconciliation Loop}\quad} \text{Desired State}$$
- **Fault Injection Verification**:
  - When the `details` Pod is forcefully terminated (`kubectl delete pod -l app=details`), the ReplicaSet Controller immediately detects `Replicas: 0 < 1`.
  - A replacement Pod transitions to `Running (2/2)` in **1.8 seconds**.
  - Client web traffic continues uninterrupted with **Zero Downtime**.

### 2. Zero-Downtime Rolling Update Sequence:
1. Spawns replacement Pods running the new version concurrently.
2. Traverses `readinessProbe` checks before adding Pod IPs to the Service Endpoints list.
3. Transmits `SIGTERM` to decommissioned Pods, completing in-flight requests before shutdown.

---

# Slide 8: Istio Service Mesh & Smart Traffic Management

### 1. Decoupled Two-Tier Istio Architecture:
- **Control Plane (`istiod`)**: Translates high-level YAML CRDs into Envoy xDS configuration; manages CA certificates.
- **Data Plane (Envoy Sidecars)**: Injected into every Pod, intercepting all Inbound (:15006) and Outbound (:15001) traffic via `iptables`.

### 2. The Core Istio CRD Triad:
- **`Gateway`**: Configures L4–L6 edge ingress entry points (Ports 80/443).
- **`VirtualService`**: Defines L7 routing rules:
  ```yaml
  match:
  - headers:
      end-user:
        exact: jason
    route:
    - destination: { host: reviews, subset: v2 } # User jason routed to black stars
  - route:
    - destination: { host: reviews, subset: v1 } # Default routed to no stars
  ```
- **`DestinationRule`**: Declares target **Subsets** (`v1`, `v2`, `v3`) mapped to Kubernetes Pod labels.

---

# Slide 9: Zero Trust Security with Transparent mTLS

### 1. Zero Trust Principles in Kubernetes:
- Internal cluster networks are fundamentally untrusted.
- Every inter-pod connection must be **Authenticated**, **Authorized**, and **Encrypted**.

### 2. Transparent mTLS Mechanics:
1. **Cryptographic Identity (SPIFFE ID)**:
   Every service account receives an immutable identity:  
   `spiffe://cluster.local/ns/default/sa/bookinfo-productpage`
2. **Automated Certificate Lifecycle**:
   `istiod` acts as a dynamic CA, issuing and rotating short-lived X.509 certificates to Envoy sidecars via Secret Discovery Service (SDS).
3. **Transparent Handshake**:
   Sidecars negotiate mutual TLS handshakes at Layer 4. Application runtimes transmit plain HTTP locally, completely unaware of wire encryption.
4. **`STRICT` PeerAuthentication**:
   Enforces mandatory mTLS across the mesh, rejecting any plaintext connection attempts.

---

# Slide 10: Observability (Prometheus & Grafana) & Trade-offs

### 1. Cloud-Native Observability & 4 Golden Signals:
- **Prometheus Pull-Based Scraping**: Periodically polls `:15090/stats/prometheus` on every Envoy sidecar without code modification.
- **Key PromQL Telemetry Queries**:
  - *Global RPS by Workload*: `sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)`
  - *P95 Latency for Productpage*: `histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{destination_workload="productpage-v1"}[1m])) by (le))`
- **Grafana Visualization**: Real-time dashboards for Istio Mesh and Service performance.

### 2. Architectural Trade-Off Matrix:

| Architectural Dimension | Primary Advantages Gained | Incurred Engineering Trade-offs |
|---|---|---|
| **Polyglot Microservices** | Domain-optimized language selection; independent deployments; small blast radius. | Multi-SDK maintenance burden, varied toolchains, and distributed debugging complexity. |
| **Envoy Sidecar Pattern** | Decouples 100% of network, security, and telemetry code from business applications. | **Network Hop Latency**: Adds $+1.5\text{ to }3.0\text{ ms}$ per call. **Memory**: $+30\text{ to }50\text{ MB}$ RAM/Pod. |
| **Zero Trust mTLS** | Automatic wire encryption and cryptographic identity via SPIFFE ID. | CPU overhead consumed by continuous TLS handshakes and payload encryption. |
| **Prometheus Telemetry** | Centralized, standardized Golden Signal monitoring across all workloads. | Periodic scraping traffic creates background network noise on large clusters. |
