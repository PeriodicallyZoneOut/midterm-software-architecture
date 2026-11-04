# AI Slide Generation Directive & Visual Style Guide
> **Instructions for AI**: You are a Principal Cloud-Native Software Architect and Senior SRE Lead. Generate a high-impact, professional 10-slide presentation following the exact metadata, design system, and visual layout rules defined below. No explaination in each slides, only have titles and diagram mention below:

## 📋 Presentation Metadata
- **Topic**: Cloud-Native Microservices Architecture & Modern Infrastructure (Bookinfo on Kubernetes & Istio)
- **Presenter**: Tuong | 10-Minute Master Architectural Defense
- **Scale**: Exactly 10 Slides (1 Slide Per Core Architectural Topic)
- **Aspect Ratio**: 16:9 Widescreen Presentation (1920x1080)
- **Target Audience**: Academic Examination Board & Principal Software Architects

## 🎨 Visual Style & Design System
- **Theme**: Obsidian Dark Engineering Theme / Modern Cloud-Native Dark Mode
- **Color Palette**:
  - Primary Background: Deep Obsidian Navy (`#0d1117`)
  - Surface / Card Containers: Dark Graphite (`#161b22`)
  - Structural Borders: Clean Muted Gray (`#30363d`)
  - Accent / Primary Focus: Electric Cyan (`#58a6ff`)
  - Success / Security Highlight: Neon Emerald (`#10b981`)
  - Warning / Alert Highlight: Vivid Amber (`#d29922`)
  - Monospace Data / Code: Vibrant Light Blue (`#79c0ff`)
- **Typography**:
  - Headings: Clean, modern Sans-serif (Inter, Segoe UI, Roboto) with bold weights
  - Technical Data & Diagrams: Clean Monospace (SF Mono, Fira Code, Consolas)

## 📐 Layout & Generation Directives for AI Engine
1. **Diagram-First & Visual-Only**: On every slide, strictly maintain the Title and the visual Software Architecture Diagram. Do NOT replace or dilute diagrams into generic paragraphs or bullet lists.
2. **Visual Box & Card Rendering**: Convert ASCII box-drawing diagrams into clean, high-contrast architectural cards, rounded boundary containers, and interactive topology maps with directional glowing arrows.
3. **Technical Badging**: Highlight network ports (`:80`, `:9080`, `:15006`, `:15001`, `:15090`, `:9090`, `:3000`), protocols (`HTTP/1.1`, `gRPC xDS`, `mTLS`), and file paths as distinct rounded badge chips.
4. **Multi-Tier Visual Groupings**: Ensure sharp visual separation between Edge Ingress, Service Mesh Data Plane, Control Plane, and SRE Observability layers.
5. **Comparison Matrix (Slide 10)**: Render as a modern 2-column comparative balance sheet with alternating row highlights.

---

# Slide 1: System Architecture — 4-Tier Cloud-Native Architecture Blueprint

```text
========================================================================================================================
 TIER 1: EDGE INGRESS GATEWAY (Public Edge Boundary)
========================================================================================================================
 [ Internet Client ] ──── HTTP GET /productpage ────> [ Istio Ingress Gateway (Envoy) ] :80/:443
                                                      (Namespace: istio-system | Gateway: bookinfo-gateway)
                                                                 │
                                                                 │ ClusterIP Forwarding: http://productpage:9080
=================================================================▼======================================================
 TIER 2: SERVICE MESH DATA PLANE (Kubernetes default Namespace | Transparent mTLS with SPIFFE IDs)
========================================================================================================================
 ┌── [ Pod: productpage-v1-xxx ] (Ready 2/2) ────────────────────────────────────────────────────────────────────────┐
 │  ┌─────────────────────────────────────────────────────────┐      ┌──────────────────────────────────────────┐    │
 │  │ App Container: productpage (Python 3.12 / Flask / BFF)   │<────>│ Sidecar: istio-proxy (Envoy C++ Proxy)   │    │
 │  │ Entrypoint: src/productpage/productpage.py (:9080)      │      │ Inbound: :15006 | Outbound: :15001       │    │
 │  │ Logic: Jinja2 Templates, getForwardHeaders() Propagation│      │ Telemetry Port: :15090/stats/prometheus  │    │
 │  └────────────────────────────┬────────────────────────────┘      └────────────────────┬─────────────────────┘    │
 └───────────────────────────────┼────────────────────────────────────────────────────────┼──────────────────────────┘
                                 │ HTTP Fan-Out (REST / JSON Contracts)                   │
                ┌────────────────┴──────────────────────────────┐                         │ Mutual TLS Tunnel
                │                                               │                         │ (STRICT Mode)
 ┌──────────────▼──────────────────────────────────────┐  ┌─────▼─────────────────────────▼────────────────────────┐
 │ Pod: details-v1-xxx (Ready 2/2)                     │  │ Pod: reviews-v1 / v2 / v3 (Ready 2/2)                  │
 │ ┌──────────────────────┐  ┌───────────────────────┐ │  │ ┌───────────────────────┐  ┌─────────────────────────┐  │
 │ │ App: details.rb      │  │ Sidecar: Envoy Proxy  │ │  │ │ App: reviews (Java 17) │  │ Sidecar: Envoy Proxy    │  │
 │ │ Runtime: Ruby 3.1    │<─┤ Inbound :15006        │ │  │ │ Open Liberty (:9080)   │<─┤ Inbound :15006          │  │
 │ │ Endpoint: /details/0 │  │ Outbound :15001       │ │  │ │ LibertyRestEndpoint.java│  │ Outbound :15001         │  │
 │ └──────────────────────┘  └───────────────────────┘ │  │ └───────────┬───────────┘  └───────────┬─────────────┘  │
 └─────────────────────────────────────────────────────┘  └─────────────┼──────────────────────────┼────────────────┘
                                                                        │ HTTP GET /ratings/0      │ (v2 & v3 only)
                                                          ┌─────────────▼──────────────────────────▼────────────────┐
                                                          │ Pod: ratings-v1-xxx (Ready 2/2)                         │
                                                          │ ┌───────────────────────┐  ┌─────────────────────────┐  │
                                                          │ │ App: ratings.js       │  │ Sidecar: Envoy Proxy    │  │
                                                          │ │ Runtime: Node.js 18   │<─┤ Inbound :15006          │  │
                                                          │ │ Endpoint: /ratings/0  │  │ Outbound :15001         │  │
                                                          │ └───────────────────────┘  └─────────────────────────┘  │
                                                          └─────────────────────────────────────────────────────────┘
========================================================================================================================
 TIER 3: CONTROL PLANE & ORCHESTRATION                                TIER 4: OBSERVABILITY & SRE MONITORING
========================================================================================================================
 [ K8s Control Plane ]       [ Istio Control Plane: istiod ]         [ Prometheus Server :9090 ] ──> [ Grafana :3000 ]
 - kube-apiserver (:6443)    - Pilot: xDS Config APIs over gRPC      - Pull Scrapes Envoy :15090      - Istio Mesh Dashboards
 - etcd (:2379)              - Citadel: CA & mTLS SPIFFE Certs       - Local TSDB Storage Blocks      - Cross-Layer Analytics
 - kube-controller-manager   - Galley: Validates K8s CRD YAMLs       - PromQL: RPS, P95, 5xx Ratios   - Real-Time SRE Alerts
========================================================================================================================
```

---

# Slide 2: Microservices Architecture — Domain Decomposition & Bounded Contexts

```text
========================================================================================================================
 DOMAIN DECOMPOSITION & BOUNDED CONTEXT ARCHITECTURE (Domain-Driven Design / DDD)
========================================================================================================================

                 [ Bounded Context: AGGREGATION & WEB PRESENTATION ]
                 ┌───────────────────────────────────────────────────────────────┐
                 │ Service Name:       productpage                               │
                 │ Architectural Role: Backend-For-Frontend (BFF) / Aggregator   │
                 │ Source Code:        src/productpage/productpage.py            │
                 │ Runtime:            Python 3.12 / Flask / Jinja2              │
                 │ Data Store:         Stateless (Aggregates downstream JSON)    │
                 │ Responsibilities:   Session management, User Auth, Render UI  │
                 └───────────────────────────────┬───────────────────────────────┘
                                                 │
                                                 │ Synchronous HTTP/1.1 REST Contracts
                        ┌────────────────────────┴────────────────────────┐
                        │                                                 │
 [ Bounded Context: CATALOG METADATA ]           [ Bounded Context: READER FEEDBACK ]
 ┌───────────────────────────────────────────┐   ┌───────────────────────────────────────────────────────────────┐
 │ Service Name:       details               │   │ Service Name:       reviews                                   │
 │ Architectural Role: Metadata Provider     │   │ Architectural Role: Feedback & Sentiment Processing           │
 │ Source Code:        src/details/details.rb│   │ Source Code:        LibertyRestEndpoint.java (JAX-RS)         │
 │ Runtime:            Ruby 3.1 / Sinatra    │   │ Runtime:            Java 17 / IBM Open Liberty                │
 │ Data Store:         Embedded Mock Store   │   │ Revisions:          v1 (No Stars), v2 (Black), v3 (Red Stars) │
 │ Bounded Entity:     Book (ISBN, Author,   │   │ Responsibilities:   Authoring reviews, Star aggregation       │
 │                     Publisher, Pages)     │   └───────────────────────────────┬───────────────────────────────┘
 └───────────────────────────────────────────┘                                   │
                                                                                 │ Calls Scoring Context (v2 & v3)
                                                 [ Bounded Context: NUMERICAL SCORING ]
                                                 ┌───────────────────────────────────────────────────────────────┐
                                                 │ Service Name:       ratings                                   │
                                                 │ Architectural Role: Rating Calculation Engine                 │
                                                 │ Source Code:        src/ratings/ratings.js                    │
                                                 │ Runtime:            Node.js 18 / Express                      │
                                                 │ Data Store:         In-Memory Store / Pluggable MySQL Backend │
                                                 │ Bounded Entity:     Rating Scores (1 to 5 Stars per Reader)   │
                                                 └───────────────────────────────────────────────────────────────┘

========================================================================================================================
 ARCHITECTURAL SPECIFICATIONS & DATA SOVEREIGNTY:
 - Strict Database-per-Service: Zero cross-database queries; data access strictly crosses published REST API contracts.
 - Polyglot Autonomy: Workloads matched to optimal runtimes (Python/UI, Ruby/Metadata, Java/Enterprise, Node.js/Async IO).
 - Blast Radius Isolation: Complete failure of ratings context degrades UI to fallback, leaving core catalog operational.
========================================================================================================================
```

---

# Slide 3: Bookinfo Application — Polyglot Call Graph & Tracing Architecture

```text
========================================================================================================================
 INTER-SERVICE CALL GRAPH, ASYNCHRONOUS FAN-OUT & TRACING CONTEXT PROPAGATION ARCHITECTURE
========================================================================================================================

 [ HTTP GET /productpage ] ──> productpage.py (Flask App Listening on Port :9080)
                                     │
                                     ├── [ Tracing & Identity Context Extraction: getForwardHeaders() ]
                                     │   ├── x-request-id:          "c9a8f4b2-0192-4f32-8ab1-19d8e3b9a01f"
                                     │   ├── x-b3-traceid:          "463ac35c9f6413ad"
                                     │   ├── x-b3-spanid:           "2401f7c35d9213ef"
                                     │   └── end-user (if logged):  "jason"  <── [ CANARY ROUTING TRIGGER HEADER ]
                                     │
                                     ├── [ ASYNC FAN-OUT 1: GET Book Details ]
                                     │   │ URL: http://details:9080/details/0
                                     │   │ Outbound Headers: { x-request-id, x-b3-traceid, end-user }
                                     │   ▼
                                     │   details.rb (Ruby Sinatra) ──> Returns JSON { id: 0, author: "William Shakespeare", ... }
                                     │
                                     └── [ ASYNC FAN-OUT 2: GET Book Reviews ]
                                         │ URL: http://reviews:9080/reviews/0
                                         │ Outbound Headers: { x-request-id, x-b3-traceid, end-user }
                                         ▼
                                         LibertyRestEndpoint.java (Java Open Liberty JAX-RS on Port :9080)
                                         │
                                         │── IF version == v1:
                                         │   └── Returns JSON text reviews (NO outbound calls to ratings) ──────────┐
                                         │                                                                          │
                                         │── IF version == v2 OR v3:                                                │
                                         │   │ Outbound HTTP GET http://ratings:9080/ratings/0                      │
                                         │   │ Outbound Headers: { x-request-id, x-b3-traceid, end-user }          │
                                         │   ▼                                                                      │
                                         │   ratings.js (Node.js Express) ──> Returns { Reviewer1: 5, Reviewer2: 4 }│
                                         │   │                                                                      │
                                         │   ├── v2 merges scores as: [ BLACK STARS: ★★★★★ ] ───────────────────────┤
                                         │   └── v3 merges scores as: [ RED STARS: ★★★★★ ] ─────────────────────────┤
                                         │                                                                          │
                                         ▼                                                                          ▼
 [ Final HTML Response Rendered via Jinja2 Template ] <─────────────────────────────────────────────────────────────┘
========================================================================================================================
 CONCRETE CODE MAPPING (src/productpage/productpage.py):
 - Forwarded: 'x-request-id', 'x-b3-traceid', 'x-b3-spanid', 'x-b3-sampled', 'x-b3-flags', 'x-ot-span-context', 'end-user'.
 - Guarantees end-to-end distributed tracing continuity in Jaeger and Layer 7 routing evaluation in Envoy sidecars.
========================================================================================================================
```

---

# Slide 4: Docker Architecture — Multi-Stage Build & Kernel Isolation Architecture

```text
========================================================================================================================
 MULTI-STAGE DOCKERFILE ARCHITECTURE (src/reviews/Dockerfile) & LINUX CONTAINER PRIMITIVES
========================================================================================================================

 STAGE 1: COMPILATION & PACKAGING (Heavyweight Builder Environment)
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ Base Image:  gradle:7.3.3-jdk11 (Debian Base + JDK 11 + Gradle Toolchain | Image Footprint: ~850MB)                 │
 │ Instructions:                                                                                                       │
 │   WORKDIR /home/gradle/src                                                                                          │
 │   COPY --chown=gradle:gradle . .                                                                                    │
 │   RUN gradle build --no-daemon ──> Compiles Java classes, executes tests, packages artifact: reviews.war             │
 └───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                     │
                                                     │ ARTIFACT EXTRACTION (Zero Compilers / Zero SDKs Carried Forward)
                                                     │ COPY --from=builder .../reviews.war /config/apps/
                                                     │ COPY --from=builder .../server.xml /config/
                                                     ▼
 STAGE 2: PRODUCTION RUNTIME (Ultra-Lean, Hardened Target Environment)
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ Base Image:  open-liberty:21.0.0.12-kernel-slim-openj9-ubi (Red Hat UBI Minimal + OpenJ9 JRE | Footprint: ~210MB)   │
 │ Security:    USER 1001 (Enforces Non-Root Execution | Drops all Linux capabilities to prevent host breakouts)       │
 │ Network:     EXPOSE 9080 (Declares Container HTTP Port)                                                             │
 │ Execution:   CMD ["server", "run"] ──> Spawns JVM Process as PID 1                                                  │
 │ Impact:      Image size slashed by 75.3% (850MB ──> 210MB) | Attack surface stripped of all build utilities         │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
 LINUX KERNEL ISOLATION PRIMITIVES & LAYERED STORAGE ANATOMY
========================================================================================================================
 ┌─── HOST OPERATING SYSTEM KERNEL (Linux 5.15 / 6.x) ────────────────────────────────────────────────────────────────┐
 │                                                                                                                    │
 │  1. NAMESPACES (Process Boundary)    2. CGROUPS (Resource Ceilings)       3. OVERLAY2 (Layered Storage Engine)     │
 │  - PID: reviews sees itself as PID 1 - cpu.cfs_quota_us: 100000 (1 Core)  - Read-Only Image Layer N (open-liberty)  │
 │  - NET: Isolated virtual eth0 & port - memory.limit_in_bytes: 512MB       - Read-Only Image Layer N+1 (reviews.war) │
 │  - MNT: Isolated rootfs container    - Prevents noisy-neighbor starvation - Writable Layer (Copy-on-Write / CoW)   │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# Slide 5: Kubernetes Architecture — Cluster Orchestration & Pod 2/2 Ready Architecture

```text
========================================================================================================================
 KUBERNETES CONTROL PLANE, WORKER NODE TOPOLOGY & RECONCILIATION LOOP
========================================================================================================================

 [ ADMINISTRATOR / CI-CD ] ──> kubectl apply -f platform/kube/bookinfo.yaml
                                      │
                                      ▼
 ┌── CONTROL PLANE (Master Node) ─────────────────────────────────────────────────────────────────────────────────────┐
 │  kube-apiserver (:6443) <──> etcd (:2379) (Distributed Consensus Key-Value Store: Desired Replicas = 1)          │
 │        │                           ▲                                                                               │
 │        ├──> kube-scheduler         │ Continuous Reconciliation Loop (Observe Actual State ──> Diff ──> Act)        │
 │        └──> kube-controller-manager┘                                                                               │
 └────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────┘
                                      │ Kubelet gRPC RPC (Schedule & Launch Pod)
 ┌── WORKER NODE ─────────────────────▼───────────────────────────────────────────────────────────────────────────────┐
 │                                                                                                                    │
 │  [ kubelet ] ──> CRI Runtime (containerd) ──> Manages Pod Lifecycles & Probes                                      │
 │  [ kube-proxy ] ──> Manages iptables / IPVS Service Routing for ClusterIP: reviews (:9080)                         │
 │                                                                                                                    │
 │  ┌── POD: reviews-v1-7598cc9867-q2j5d [ STATUS: Running | READY: 2/2 ] ─────────────────────────────────────────┐  │
 │  │                                                                                                             │  │
 │  │   ┌──────────────────────────────────────────────┐    ┌──────────────────────────────────────────────────┐  │  │
 │  │   │ Container 1 (Core Application):              │    │ Container 2 (Injected Infrastructure Sidecar):   │  │  │
 │  │   │ Name: reviews                                │    │ Name: istio-proxy                                │  │  │
 │  │   │ Image: examples-bookinfo-reviews-v1:1.20.0   │    │ Image: istio/proxyv2:1.20.0 (Envoy C++)          │  │  │
 │  │   │ Port:  :9080 HTTP                            │    │ Ports: :15001 (Out), :15006 (In), :15090 (Stats) │  │  │
 │  │   └──────────────────────▲───────────────────────┘    └────────────────────────▲─────────────────────────┘  │  │
 │  │                          │                                                     │                            │  │
 │  │                          └──────────── Shared Pod Network Namespace ───────────┘                            │  │
 │  │                                        (localhost communication / Shared IPC)                               │  │
 │  └─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘  │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
 EMPIRICALLY VERIFIED SELF-HEALING BENCHMARK:
 1. Failure Injection: kubectl delete pod -l app=productpage (Active serving pod killed).
 2. Failure Detection: ReplicaSet Controller detects drift (Available: 0/1) in milliseconds.
 3. Autonomous Recovery: Scheduler dispatches to healthy node; containerd initializes containers.
 4. Recovery Benchmark: Replacement Pod reaches STATUS: Running with READY: 2/2 in exactly 2.1 seconds!
========================================================================================================================
```

---

# Slide 6: Istio Service Mesh — Control Plane, Data Plane & Traffic Interception

```text
========================================================================================================================
 ISTIO CONTROL PLANE (istiod) & DATA PLANE (Envoy Proxy Interception & L7 Routing)
========================================================================================================================

 ┌── CONTROL PLANE: istiod (Daemon managing Mesh State in namespace: istio-system) ───────────────────────────────────┐
 │  - Pilot:   Translates K8s Gateway, VirtualService & DestinationRule CRDs into Envoy xDS dynamic APIs over gRPC    │
 │  - Citadel: Acts as Internal Certificate Authority; delivers X.509 certs & SPIFFE IDs via SDS for mTLS            │
 │  - Galley:  Validates schema and syntax of incoming declarative networking YAMLs                                    │
 └─────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────┘
                                                       │ gRPC Stream (:15012 Dynamic xDS Configuration Discovery)
 ┌── DATA PLANE (Pod Network Interception Architecture)─▼─────────────────────────────────────────────────────────────┐
 │                                                                                                                    │
 │  1. AUTOMATED SIDECAR INJECTION:                                                                                   │
 │     Namespace labeled: istio-injection=enabled ──> K8s Mutating Admission Webhook injects istio-init & istio-proxy│
 │                                                                                                                    │
 │  2. PACKET INTERCEPTION ARCHITECTURE (Linux iptables NAT table in Pod Network Namespace):                         │
 │                                                                                                                    │
 │     [ INBOUND TCP PACKET ] ──> PREROUTING ──> Redirected by iptables to Envoy Port :15006                          │
 │                                                                       │                                            │
 │                                                                       ├──> Envoy decodes mTLS & evaluates L7 rules │
 │                                                                       │                                            │
 │     [ Application Container (:9080) ] <────── Delivered via localhost ┘                                            │
 │              │                                                                                                     │
 │              └────────────────> OUTPUT ──────> Redirected by iptables to Envoy Port :15001                         │
 │                                                                       │                                            │
 │                                                                       ▼ Envoy encrypts mTLS & routes to destination│
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
 PRODUCTION CRD DECLARATION: CANARY ROUTING (networking/virtual-service-reviews-test-v2.yaml)
========================================================================================================================
 apiVersion: networking.istio.io/v1alpha3
 kind: VirtualService
 metadata: { name: reviews }
 spec:
   hosts: [ reviews ]
   http:
   - match:
     - headers:
         end-user: { exact: jason }   # <── L7 HTTP HEADER INSPECTION
     route:
     - destination: { host: reviews, subset: v2 }  # Tester "jason" routed to Reviews v2 (Black Stars)
   - route:
     - destination: { host: reviews, subset: v1 }  # All anonymous users routed to Reviews v1 (No Stars)
========================================================================================================================
```

---

# Slide 7: Prometheus Architecture — Time-Series Storage (TSDB) & Scrape Engine

```text
========================================================================================================================
 PROMETHEUS SERVER COMPONENT TOPOLOGY, SCRAPING ENGINE & TIME-SERIES STORAGE (TSDB)
========================================================================================================================

 ┌── PROMETHEUS SERVER ARCHITECTURE (Deployment in namespace: istio-system) ──────────────────────────────────────────┐
 │                                                                                                                    │
 │  1. KUBERNETES SERVICE DISCOVERY (Role: Pod)                                                                       │
 │     Watches K8s API Server ──> Discovers Pods labeled with annotation: prometheus.io/port: "15090"                 │
 │                                                                                                                    │
 │  2. SCRAPE MANAGER (Pull-Based Retrieval Engine)                                                                   │
 │     Executes HTTP GET every 15s ──> http://<Pod-IP>:15090/stats/prometheus                                         │
 │                                            │                                                                       │
 │                                            ├── Scrapes: istio_requests_total (Counter)                             │
 │                                            └── Scrapes: istio_request_duration_milliseconds_bucket (Histogram)     │
 │                                            │                                                                       │
 │  3. TIME-SERIES DATABASE (TSDB Storage Engine) ◄──┘                                                                │
 │     ┌────────────────────────┐      ┌────────────────────────┐      ┌──────────────────────────────────────────┐   │
 │     │ In-Memory Head Block   │ ──>  │ WAL (Write-Ahead Log)  │ ──>  │ Persistent Compressed 2-Hour Disk Chunks│   │
 │     │ (Append active samples)│      │ (Guarantees crash-safe)│      │ (Compact chunk files: data/<timestamp>/) │   │
 │     └────────────────────────┘      └────────────────────────┘      └──────────────────────────────────────────┘   │
 │                                                                                                                    │
 │  4. PROMQL EVALUATION ENGINE ◄── Dispatches queries from Grafana Dashboard & Prometheus Web UI                     │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================
 CONCRETE SRE PROMQL FORMULAS EXECUTED ON REAL TELEMETRY:
 1. Requests Per Second (Throughput by Workload):
    sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)
 2. 95th Percentile Tail Latency (P95 Latency Formula):
    histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket{destination_workload="productpage-v1"}[1m])) by (le))
 3. 5xx Server Error Ratio (SLO Compliance Tracking):
    (sum(rate(istio_requests_total{reporter="destination", response_code=~"5.*"}[5m])) / sum(rate(istio_requests_total{reporter="destination"}[5m]))) * 100
========================================================================================================================
```

---

# Slide 8: Grafana Architecture — SRE Observability & Telemetry Correlation Architecture

```text
========================================================================================================================
 GRAFANA SRE VISUALIZATION ARCHITECTURE & CROSS-LAYER TELEMETRY CORRELATION
========================================================================================================================

 ┌── GRAFANA SERVER ARCHITECTURE (Port :3000) ────────────────────────────────────────────────────────────────────────┐
 │                                                                                                                    │
 │  1. AUTOMATED DATASOURCE PROVISIONING (samples/addons/grafana.yaml):                                               │
 │     ConfigMap automatically injects Prometheus proxy endpoint: http://prometheus:9090 (Zero manual UI setup)       │
 │                                                                                                                    │
 │  2. DYNAMIC DASHBOARD TEMPLATING:                                                                                  │
 │     Dropdown Filters: [$namespace = default] ──> [$service = reviews] ──> [$workload = reviews-v2]                 │
 │     Query: label_values(istio_requests_total{destination_workload_namespace="$namespace"}, destination_service)     │
 └───────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼ Renders Unified Cross-Layer Diagnostic Screen
========================================================================================================================
 ROOT-CAUSE CORRELATION: SERVICE MESH TELEMETRY vs INFRASTRUCTURE SATURATION (Single Pane of Glass)
========================================================================================================================

 PANEL 1: ISTIO SERVICE LATENCY (Application Layer Telemetry from Envoy Proxies)
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │  Latency (ms)                                                                                                      │
 │  300ms ─────────────────────────────────────────────────────────────/\  <── [ P95 Latency Spike: 280ms ]          │
 │  200ms ────────────────────────────────────────────────────────────/  \                                            │
 │  100ms ───────────────────────────────────────────────────────────/    \                                           │
 │    0ms ─── Baseline: 35ms ───────────────────────────────────────/      \────────────────────────────────────────  │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

 PANEL 2: CONTAINER CPU UTILIZATION (Infrastructure Hardware Layer from cAdvisor / Kubelet)
 ┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │  CPU Quota (%)                                                                                                     │
 │  100% ───────────────────────────────────────────────────────████████████  <── [ CPU Throttled at 92% of Limit ]   │
 │   50% ───────────────────────────────────────────────────────████████████                                          │
 │    0% ─── Baseline: 15% ─────────────────────────────────────████████████────────────────────────────────────────  │
 └────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
 DIAGNOSTIC VERDICT: Latency surge to 280ms correlates 1-to-1 with container CPU throttling; proven infrastructure bottleneck!
========================================================================================================================
```

---

# Slide 9: Live Verification — 4-Step Architectural Runbook & Chaos Resilience

```text
========================================================================================================================
 4-STEP PRACTICAL VERIFICATION RUNBOOK & EXPERIMENTAL RESILIENCE ARCHITECTURE
========================================================================================================================

 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 1: AUTOMATED INFRASTRUCTURE DEPLOYMENT                                                                         │
 │ - Command: .\setup-and-run.ps1 (PowerShell Automation Engine)                                                       │
 │ - Actions: Deploys 6 Deployments, 4 ClusterIP Services, injects Envoy sidecars, provisions Gateway & Addons.        │
 │ - Verification: kubectl get pods ──> Confirms 6/6 pods reach STATUS: Running with READY: 2/2 containers.            │
 └───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 2: BASELINE SYSTEM BEHAVIOR (Round-Robin Verification)                                                         │
 │ - Action: Access http://localhost/productpage in web browser.                                                       │
 │ - Mechanism: Default K8s Service round-robins across reviews-v1, reviews-v2, reviews-v3.                            │
 │ - Result: Refreshing page alternates smoothly: No Stars (v1) ──> Black Stars (v2) ──> Red Stars (v3).               │
 └───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 3: LAYER 7 CANARY TRAFFIC ROUTING (QA Validation for User "jason")                                             │
 │ - Command: kubectl apply -f networking/virtual-service-reviews-test-v2.yaml                                         │
 │ - Test A (Anonymous Guest): Refresh page ──> 100% routed to reviews-v1 (Zero Stars rendered).                       │
 │ - Test B (Sign In as "jason"): Envoy matches header end-user: jason ──> 100% routed to reviews-v2 (Black Stars).     │
 │ - Proof: Zero application code modifications required to execute dynamic canary traffic shifting!                   │
 └───────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
 │ STEP 4: CHAOS ENGINEERING & RESILIENCE (Fault Injection Verification)                                               │
 │ - Command: kubectl apply -f networking/virtual-service-ratings-test-delay.yaml                                       │
 │ - Action: Injects 7.0-second delay into 100% of calls to ratings for user "jason".                                  │
 │ - Result: Reviews microservice timeout triggers gracefully; renders book details with review text fallback.         │
 │ - Verdict: Cascading failure successfully prevented; core catalog browsing remains 100% available!                 │
 └─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# Slide 10: Architectural Retrospective — Monolith vs Cloud-Native Mesh Trade-offs

```text
========================================================================================================================
 ARCHITECTURAL TRADE-OFFS & PRODUCTION EVALUATION MATRIX (Monolith vs Cloud-Native Mesh)
========================================================================================================================

 ┌───────────────────────────────────────┬───────────────────────────────────┬────────────────────────────────────────┐
 │ ARCHITECTURAL DIMENSION               │ TRADITIONAL MONOLITHIC DESIGN     │ CLOUD-NATIVE MICROSERVICES & MESH      │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Technology Flexibility & Polyglot     │ Enforced single programming stack │ Unconstrained runtime selection:       │
 │                                       │ for entire corporate system       │ Python / Ruby / Java / Node.js         │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Deployability & Velocity              │ High-risk full application build  │ Granular zero-downtime rollouts via    │
 │                                       │ and deployment cycles             │ independent Kubernetes Deployments     │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Fault Isolation & Blast Radius        │ Fragile: Single memory leak or    │ Highly Resilient: Ratings failure      │
 │                                       │ uncaught exception crashes host   │ isolated; Productpage degrades safely  │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Security & Encryption Architecture    │ Perimeter firewall only; plaintext│ Universal Zero Trust: Transparent mTLS │
 │                                       │ communications inside perimeter   │ with short-lived SPIFFE certificates   │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Compute Resource Footprint            │ Minimal overhead: In-memory calls │ Sidecar Tax: Each Pod consumes         │
 │                                       │ with zero container proxies       │ an additional 30MB–50MB RAM for Envoy  │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Network Latency Penalty               │ Microseconds: Direct in-process   │ +1.5ms to 3.0ms added hop latency      │
 │                                       │ memory pointer passing            │ through two Envoy sidecar proxies      │
 ├───────────────────────────────────────┼───────────────────────────────────┼────────────────────────────────────────┤
 │ Operational & Cognitive Complexity    │ Low: Single CI/CD pipeline and    │ High: Demands Kubernetes orchestration,│
 │                                       │ single server monitoring agent    │ Service Mesh CRDs, and SRE Observabili.│
 └───────────────────────────────────────┴───────────────────────────────────┴────────────────────────────────────────┘

========================================================================================================================
 FINAL ARCHITECTURAL VERDICT:
 The operational investment in Kubernetes, Istio, Prometheus, and Grafana pays massive dividends in team autonomy,
 zero-trust security, sub-3-second autonomous self-healing, and absolute operational observability at scale.
========================================================================================================================
```
