# Cloud-Native Microservices Architecture & Infrastructure: End-to-End Defense
**Presenter**: Tuong | Master Architectural Presentation (10 Minutes Total — 1 Slide Per Topic)
**Format**: 10 Slides (Exactly 60 seconds per slide)
**Design Theme**: Modern Dark Mode (#0d1117 background, cyan/blue accent #58a6ff, high-contrast architecture cards)
**Target Tool**: Optimized for direct paste into **Gamma.app**, **Tome.app**, or **SlidesGPT**

---

# Slide 1: System Overview — The Cloud-Native Architectural Blueprint
**Topic**: High-Level System Architecture & End-to-End Topology
**Layout**: Top-Down Layered Architecture Diagram with 4 Distinct Tiers
**Visual Prompt**: Modern enterprise cloud architecture diagram with 4 distinct horizontal tiers: Client Layer, L7 Ingress Gateway, Service Mesh Data Plane (4 polyglot microservices in Kubernetes pods with sidecars), and Observability Stack (Prometheus & Grafana). Cyan and indigo neon data lines on a dark obsidian background.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ 1. EDGE INGRESS LAYER: Istio Ingress Gateway (Port 80/443)             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP /productpage
┌───────────────────────────────────▼────────────────────────────────────┐
│ 2. APPLICATION MESH LAYER (Kubernetes Pods with Envoy Sidecars)        │
│                                                                        │
│   [ productpage ] (Python 3.12 / Flask) ── Aggregator & Web UI         │
│          │                                                             │
│          ├──> [ details ] (Ruby / Sinatra) ── Book Metadata            │
│          └──> [ reviews ] (Java 17 / Open Liberty) ── Reviews v1/v2/v3 │
│                     │                                                  │
│                     └──> [ ratings ] (Node.js 18) ── Star Ratings      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Envoy Telemetry (:15090/stats)
┌───────────────────────────────────▼────────────────────────────────────┐
│ 3. OBSERVABILITY LAYER: Prometheus TSDB & SRE Grafana Dashboards       │
└────────────────────────────────────────────────────────────────────────┘
```

- **Architectural Vision**: Complete transition from brittle monolith to self-healing, polyglot microservices with zero-trust security and real-time observability.
- **Presenter Script (1:00)**: "Good morning Committee. I am Tuong, presenting the software architecture of our cloud-native microservices platform. This architecture integrates four core polyglot microservices running in Kubernetes, governed by an Istio Service Mesh, and continuously monitored through Prometheus and Grafana. Today, I will walk you through each architectural layer in 10 minutes."

---

# Slide 2: Microservices — Domain Decomposition & Architectural Principles
**Topic**: Microservices Architecture & Domain-Driven Design (DDD)
**Layout**: 2 Columns (Left: Bounded Context Domain Map | Right: Architectural Principles)
**Visual Prompt**: Domain-driven design breakdown showing Monolith decomposing into 4 clean, isolated Bounded Contexts with discrete boundaries and REST API contracts.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   DOMAIN-DRIVEN DESIGN BOUNDARIES                      │
│                                                                        │
│   ┌───────────────────────────┐     ┌──────────────────────────────┐   │
│   │ CATALOG BOUNDED CONTEXT   │     │ FEEDBACK BOUNDED CONTEXT     │   │
│   │ Service: details (Ruby)   │     │ Service: reviews (Java)      │   │
│   │ Entity: Book Metadata     │     │ Entity: Reader Commentary    │   │
│   └───────────────────────────┘     └──────────────┬───────────────┘   │
│                                                    │ REST              │
│   ┌───────────────────────────┐     ┌──────────────▼───────────────┐   │
│   │ AGGREGATION CONTEXT       │     │ SCORING BOUNDED CONTEXT      │   │
│   │ Service: productpage (Py) │     │ Service: ratings (Node.js)   │   │
│   │ Pattern: Backend-for-Front│     │ Entity: 1-5 Star Ratings     │   │
│   └───────────────────────────┘     └──────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

- **Core Architectural Patterns**:
  - **Single Responsibility Principle (SRP)**: Each service strictly owns a single business capability.
  - **Database-per-Service**: Services maintain strict data sovereignty; direct database sharing is strictly prohibited.
  - **Polyglot Design**: Right runtime for each workload (Python for templating, Ruby for metadata, Java for enterprise business logic, Node.js for async I/O).
- **Presenter Script (2:00)**: "In Slide 2, we see how Domain-Driven Design eliminates monolithic coupling. We decompose the bookstore domain into four distinct Bounded Contexts. Each service is fully autonomous, communicates strictly via REST contracts, and encapsulates its own domain model. This guarantees that failure in ratings cannot bring down the entire catalog."

---

# Slide 3: Bookinfo Application — Polyglot Implementation Architecture
**Topic**: The Bookinfo Application Implementation & Inter-Service Wiring
**Layout**: 2 Columns (Left: Fan-Out Aggregator Flow | Right: Code Architecture)
**Visual Prompt**: Sequence diagram showing asynchronous fan-out from productpage to details and reviews, followed by reviews fetching ratings, with trace headers propagated along all hops.

```text
[ Client ] ──> [ productpage.py (Flask) ]
                      │
                      ├── (Async GET) ──> [ details.rb (Sinatra) ] :9080
                      └── (Async GET) ──> [ reviews / LibertyRestEndpoint.java ] :9080
                                                │ (v2 & v3 only)
                                                └── (Async GET) ──> [ ratings.js ] :9080
```

- **Architectural Mechanics in Code**:
  - **Aggregator Pattern (`productpage.py`)**: Concurrently dispatches asynchronous HTTP queries to downstream services and merges JSON payloads into Jinja2 templates.
  - **Evolutionary Versioning (`LibertyRestEndpoint.java`)**: A single Java codebase dynamically toggles between v1 (no stars), v2 (black stars), and v3 (red stars) based on environment configuration.
  - **Trace Propagation (`getForwardHeaders`)**: Crucial architectural hook forwarding `x-request-id` and `end-user: jason` across hops for distributed tracing and L7 routing.
- **Presenter Script (3:00)**: "Slide 3 presents the concrete implementation of the Bookinfo application. The productpage service implements the Aggregator pattern, querying details and reviews in parallel. Notice our implementation of getForwardHeaders: it actively propagates tracing IDs and user identity down the call chain, providing the contextual fuel required for Istio's intelligent routing."

---

# Slide 4: Docker — Containerization & Multi-Stage Build Architecture
**Topic**: Docker Container Architecture, Linux Kernel Primitives & Multi-Stage Builds
**Layout**: 2 Columns (Left: Multi-Stage Build Flow | Right: Kernel Isolation Primitives)
**Visual Prompt**: Diagram showing Docker multi-stage compilation: Heavy 850MB Gradle builder stage stripping away compilers and delivering a lean 210MB Open Liberty runtime container running as non-root user 1001.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ MULTI-STAGE COMPILATION ARCHITECTURE (src/reviews/Dockerfile)          │
│                                                                        │
│   STAGE 1: BUILDER (gradle:7.3.3-jdk11)                                │
│   [ Full Source Code ] + [ Gradle Toolchain ] ──> compile reviews.war  │
│                                                          │             │
│                                      COPY --from=builder │ (.war only) │
│                                                          ▼             │
│   STAGE 2: PRODUCTION RUNTIME (open-liberty:kernel-slim)               │
│   [ reviews.war ] + [ server.xml ] (Zero Compilers / Non-Root 1001)    │
│   Result: Image Footprint Slashed from 850MB ──> 210MB (75% Reduction) │
└────────────────────────────────────────────────────────────────────────┘
```

- **Linux Kernel Primitives**: Namespaces (PID, NET, MNT process isolation), cgroups (strict CPU/RAM quotas), Overlay2 (Copy-on-Write immutable image layers).
- **Security & Caching**: Non-root execution (`USER 1001`) prevents container breakout attacks; manifests copied prior to source code in Dockerfiles cuts CI/CD rebuilds from 3m to 5s.
- **Presenter Script (4:00)**: "In Slide 4, we examine containerization architecture. A common anti-pattern is shipping compilers to production. We architected a Multi-Stage Dockerfile for reviews: Stage 1 builds the binary; Stage 2 extracts only the war file into a stripped runtime. This reduced our image size from 850MB to 210MB and eliminated attack surfaces."

---

# Slide 5: Kubernetes — Cluster Orchestration & Self-Healing Architecture
**Layout**: 2 Columns (Left: Control Plane vs Worker Topology | Right: The 2/2 Ready Pod Architecture)
**Visual Prompt**: Kubernetes cluster diagram showing Control Plane API server and etcd coordinating worker nodes, zooming into a Pod containing both the app container and the Envoy sidecar container sharing localhost.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   KUBERNETES ORCHESTRATION ARCHITECTURE                │
│                                                                        │
│   [ CONTROL PLANE: apiserver ──> etcd ──> scheduler ──> controller ]   │
│                                    │ Reconciliation Loop (Desired State)│
│   ┌────────────────────────────────▼───────────────────────────────┐   │
│   │ WORKER NODE (kubelet + kube-proxy)                             │   │
│   │                                                                │   │
│   │   POD: productpage-v1-xxx [ READY 2/2 ]                        │   │
│   │   ┌───────────────────────────┬────────────────────────────┐   │   │
│   │   │ Container 1 (App):        │ Container 2 (Sidecar):     │   │   │
│   │   │ Python / Flask (:9080)    │ istio-proxy / Envoy        │   │   │
│   │   └─────────────▲─────────────┴─────────────▲──────────────┘   │   │
│   │                 │ localhost (:15001/:15006) │                  │   │
│   │                 └───────────────────────────┘                  │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

- **Declarative Reconciliation Loop**: Desired state declared in `platform/kube/bookinfo.yaml` (Deployments, ClusterIP Services). Controllers continuously reconcile current state.
- **Autonomous Self-Healing**: Health probes (Startup, Liveness, Readiness). When a Pod is terminated, ReplicaSets reschedule a replacement achieving **2/2 Ready in 2.1 seconds**.
- **Presenter Script (5:00)**: "Slide 5 covers Kubernetes orchestration. We encapsulate services into atomic Pod units running two containers: the application and the Envoy sidecar proxy. Kubernetes continuously executes its reconciliation loop. When a pod crashes, the ReplicaSet controller detects the drift and restores a healthy 2/2 ready replacement within 2.1 seconds."

---

# Slide 6: Istio — Service Mesh Control Plane & Data Plane Architecture
**Topic**: Service Mesh Architecture, Transparent Packet Interception & L7 Routing
**Layout**: 2-Tier Architecture Stack (Control Plane on Top | Data Plane Envoy Mesh Below)
**Visual Prompt**: Istio architecture diagram: Control Plane istiod streaming xDS configurations over gRPC down to Envoy proxies, with Linux iptables redirecting incoming port 9080 traffic to port 15006 transparently.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                 CONTROL PLANE: istiod (Pilot, Citadel, Galley)         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ gRPC xDS Dynamic Configuration APIs
┌───────────────────────────────────▼────────────────────────────────────┐
│                 DATA PLANE: Transparent Envoy Sidecar Mesh             │
│                                                                        │
│   [ Inbound Traffic ] ──> iptables rule ──> Envoy Port :15006          │
│                                                  │                     │
│                                                  ▼ mTLS / L7 Routing   │
│   [ Outbound Traffic ] <── iptables rule <── Envoy Port :15001         │
└────────────────────────────────────────────────────────────────────────┘
```

- **Decoupling Network Concerns from Code**: Zero lines of routing or encryption code in application services.
- **Core Custom Resource Definitions (CRDs)**:
  - **Gateway (`bookinfo-gateway.yaml`)**: Edge cluster admission on port 80.
  - **DestinationRule (`destination-rule-all.yaml`)**: Defines subsets `v1`, `v2`, `v3` and mTLS policies.
  - **VirtualService (`virtual-service-reviews-test-v2.yaml`)**: L7 Canary rule routing header `end-user: jason` to `v2` (black stars) while general users stay on `v1`.
- **Zero Trust Security**: Transparent mutual TLS (mTLS) with cryptographic SPIFFE IDs and `STRICT` peer authentication.
- **Presenter Script (6:00)**: "Slide 6 illustrates the Istio Service Mesh architecture. Istio cleanly decouples L7 networking from code. Istiod translates declarative YAML into Envoy xDS APIs. Using iptables, all inbound packets are hijacked into Envoy port 15006. This enables Canary releases: by simply matching the end-user: jason header in a VirtualService, we route testers to reviews v2 without modifying a single line of Java code."

---

# Slide 7: Prometheus — Time-Series Monitoring & Pull-Based Scrape Architecture
**Topic**: Systems Metrics Architecture, TSDB Storage & PromQL Engine
**Layout**: 2 Columns (Left: Prometheus Server Data Flow | Right: PromQL Formulas)
**Visual Prompt**: Prometheus scraping engine polling Envoy proxies on port 15090, writing to local TSDB blocks, and serving PromQL calculations to Grafana.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                     PROMETHEUS TSDB ARCHITECTURE                       │
│                                                                        │
│   [ Target Discovery ] ──> [ Scrape Manager ]                          │
│                                   │ HTTP Pull (:15090/stats every 15s) │
│                                   ▼                                    │
│                            [ Local TSDB Blocks ]                       │
│                                   │                                    │
│                                   ▼                                    │
│                            [ PromQL Engine ] ──> Instant/Range Vectors │
└────────────────────────────────────────────────────────────────────────┘
```

- **The Resilient Pull Model**: Prevents cascading DDoS outages common in push architectures during cluster incidents.
- **Scraping Envoy Sidecars (`samples/addons/prometheus.yaml`)**: Prometheus scrapes `:15090/stats/prometheus` directly from Envoy without needing application-level instrumentation.
- **Core PromQL Golden Signals**:
  - **Throughput (RPS)**: `sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)`
  - **Tail Latency (P95)**: `histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le))`
  - **Error Budget (5xx)**: `(sum(rate(...{response_code=~"5.*"}[5m])) / sum(rate(...[5m]))) * 100`
- **Presenter Script (7:00)**: "In Slide 7, we examine our monitoring architecture with Prometheus. Rather than pushing metrics, Prometheus uses a resilient pull model, scraping Envoy's telemetry port 15090 every 15 seconds. Using PromQL, we calculate real-time Requests Per Second and P95 latency percentiles. Notice we do not use mean latency: histogram quantiles expose tail latency that averages conceal."

---

# Slide 8: Grafana — SRE Observability & Telemetry Correlation Architecture
**Topic**: Grafana Visualization Architecture, Dynamic Dashboards & Cross-Layer Correlation
**Layout**: 2-Panel Stack (Top: Istio Service Telemetry | Bottom: Node Hardware Saturation)
**Visual Prompt**: Grafana command dashboard showing an upper graph of traffic burst to 50 req/s aligning with a lower graph of container CPU spiking from 15% to 92%, proving CPU saturation as the root cause of latency.

```text
┌────────────────────────────────────────────────────────────────────────┐
│ TIER 1: SERVICE MESH TELEMETRY (Istio Service Dashboard)               │
│ Traffic Burst: 10 req/s  ──>  50 req/s (Spike)                         │
│ P95 Latency:   35ms      ──>  280ms                                    │
├────────────────────────────────────────────────────────────────────────┤
│ TIER 2: INFRASTRUCTURE SATURATION (cAdvisor Container Metrics)         │
│ Container CPU: 15%       ──>  92% (CPU Throttling Threshold Reached)   │
│ Container RAM: 64MB      ──>  118MB                                    │
└────────────────────────────────────────────────────────────────────────┘
```

- **Config-as-Code Provisioning (`samples/addons/grafana.yaml`)**: DataSources and Istio dashboards mounted automatically via ConfigMaps at startup.
- **Dynamic Templating**: Variables (`$namespace`, `$service`, `$workload`) allow a single dashboard definition to adapt dynamically to all cluster services.
- **Root-Cause Telemetry Correlation**: By placing network latency panels directly above container CPU panels, SREs instantly verify whether latency spikes stem from code deadlocks or CPU throttling.
- **Presenter Script (8:00)**: "Slide 8 demonstrates Grafana's visualization architecture. Grafana serves as our SRE Single Pane of Glass. By correlating Istio's L7 request latency with cAdvisor's container CPU metrics on a single screen, we solve the classic incident mystery: when P95 latency jumps to 280ms, we immediately see container CPU hitting 92%, pinpointing CPU throttling as the root cause."

---

# Slide 9: Live Verification — 4-Step End-to-End Architectural Demonstration
**Topic**: Practical System Verification, Chaos Testing & Resilience Validation
**Layout**: 4 Sequenced Milestone Cards
**Visual Prompt**: 4-step execution timeline: Automated Deployment ➔ Baseline Round-Robin ➔ Canary User Jason Black Stars ➔ Fault Injection 7s Latency Fallback.

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   STEP 1     │     │   STEP 2     │     │   STEP 3     │     │   STEP 4     │
│ Automated    │────>│ Baseline     │────>│ Canary       │────>│ Fault        │
│ Bootstrap    │     │ Verification │     │ Routing      │     │ Injection    │
│ .\setup-     │     │ Round-Robin  │     │ User "jason" │     │ 7s Delay     │
│ and-run.ps1  │     │ v1 / v2 / v3 │     │ v2 BlackStar │     │ Fallback OK  │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

- **Step 1: Automated Deployment**: `setup-and-run.ps1` bootstraps K8s manifests, injects Envoy sidecars, and provisions Prometheus/Grafana.
- **Step 2: Baseline Validation**: Access `http://localhost/productpage`. Browser refreshes alternate between reviews v1, v2, and v3 via K8s round-robin.
- **Step 3: Canary L7 Routing**: Apply `virtual-service-reviews-test-v2.yaml`. Logging in as user `jason` exclusively renders v2 (Black Stars); logging out instantly reverts to v1 (No Stars).
- **Step 4: Chaos Resilience**: Inject 7-second delay on `ratings`. Productpage gracefully serves fallback text without hanging or crashing!
- **Presenter Script (9:00)**: "Slide 9 outlines our live verification runbook. First, our automated script provisions the entire stack. Second, baseline traffic alternates across all three review versions. Third, we apply our Canary rule: logging in as user jason consistently displays v2 Black Stars, while guest visitors see v1. Finally, we inject a 7-second fault into ratings; the system falls back gracefully, proving resilience against cascading failures."

---

# Slide 10: Architectural Retrospective — Monolith vs Cloud-Native Mesh
**Topic**: Comprehensive Architectural Trade-offs & Production Evaluation
**Layout**: 2-Column Balance Sheet (Architectural Superpowers vs Concrete System Costs)
**Visual Prompt**: Balance scales weighing Architectural Agility against Operational Infrastructure Complexity, with Cloud-Native best practices mitigating costs.

| Architectural Dimension | Traditional Monolith | Cloud-Native Microservices & Mesh |
|---|---|---|
| **Technology Strategy** | Single language lock-in | **Polyglot Flexibility**: Optimal runtime per service |
| **Deployability** | High-risk full-app redeployment | **Independent Deployability**: Zero downtime rollouts |
| **Failure Blast Radius** | Cascading: single bug crashes process | **Isolated**: Ratings failure leaves catalog operational |
| **Security Architecture** | Perimeter firewall only | **Zero Trust**: Universal mTLS & SPIFFE workload identity |
| **Operational Overhead** | Low (Single binary, single server) | **High**: Demands K8s orchestration & Istio service mesh |
| **Network Hop Latency** | Near zero (in-memory calls) | **Overhead**: +1.5ms to 3ms per sidecar hop |

- **Conclusion**: The architectural benefits of resilience, independent velocity, and zero-trust security overwhelmingly justify the operational investments in Kubernetes and Istio.
- **Presenter Script (10:00)**: "To conclude in Slide 10: migrating from a Monolith to a Cloud-Native Mesh is an engineering trade-off. We pay a budget of 30MB of RAM per sidecar and 1.5ms of hop latency. In return, we achieve total team autonomy, zero-trust cryptographic security, sub-3-second self-healing, and complete operational observability. Thank you Committee, I am now ready for your questions."

