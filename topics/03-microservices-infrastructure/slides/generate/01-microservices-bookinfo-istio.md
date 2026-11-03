# Master Deck 1: Microservices Architecture, Bookinfo & Istio Service Mesh
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Cloud-Native Engineering, Cyan Glow (#58a6ff) & Slate Navy

---

# Slide 1: The Monolith Crisis & Microservices Principles
**Layout**: 2 Columns (Left: Monolith Pain Points | Right: Microservices Architecture)
**Visual**: A cracked legacy monolith contrasting with an agile network of independent services communicating over APIs.

- **The Monolith Bottleneck**:
  - **Coupled Codebase**: Skyrocketing build and test times; high cognitive overload for engineering teams.
  - **Deployment Paralysis**: A minor bug in a non-critical module risks crashing the entire system (Single Point of Failure).
  - **Monolithic Scaling**: Scaling a single compute-heavy feature forces expensive horizontal replication of the entire application.
- **The Microservices Paradigm Shift**:
  - Decompose systems into autonomous services structured around **Bounded Contexts** (Domain-Driven Design).
  - Enforce **Single Responsibility (SRP)**: Each service owns its domain logic and data lifecycle.

---

# Slide 2: Architectural Comparison: Monolith vs Microservices
**Layout**: 3-Column Comparison Table
**Visual**: Matrix diagram comparing data sovereignty, deployment boundaries, and operational complexity.

| Architectural Dimension | Traditional Monolith | Modular Monolith | Microservices Architecture |
|---|---|---|---|
| **Data Storage** | 1 Shared Relational Database | 1 Database with logical schema boundaries | **Database-per-Service** (Full Data Sovereignty) |
| **Communication** | In-memory function invocations | Internal modular API calls in memory | **Distributed Network** (REST HTTP / gRPC / Events) |
| **Deployability** | Full-app redeployment required | Full-process redeployment required | **Independent Deployability** per Pod / Service |
| **Fault Isolation** | Poor (Single bug crashes host process) | Moderate (Isolated logic, shared memory) | **High** (Blast radius strictly contained) |
| **Operational Overhead** | Low (Single pipeline, single binary) | Moderate | **High** (Requires K8s, Service Mesh, Observability) |

---

# Slide 3: The Bookinfo System: A Polyglot Microservices Topology
**Layout**: Hierarchical Tree Topology Diagram from Edge Ingress down to Backends
**Visual**: Client ➔ Istio Gateway ➔ productpage (Python) branching to details (Ruby) and reviews (Java) ➔ ratings (Node.js).

```text
[ Client Web Browser ]
          │
          ▼
[ Istio Ingress Gateway :80 ]
          │
          ▼
[ productpage (Python/Flask) ]  <── Web Frontend & Content Aggregator
          ├───> [ details (Ruby/Sinatra) ]  <── Book Metadata Service
          └───> [ reviews (Java/OpenLiberty) ]  <── Customer Reviews Service
                    └───> [ ratings (Node.js/Express) ]  <── Star Ratings (v2 & v3)
```
- **The Polyglot Advantage**: 4 languages chosen for domain fit (Python rapid UI, Ruby lightweight data, Java enterprise concurrency, Node.js non-blocking I/O).
- Zero shared runtime libraries: All inter-service communication governed strictly by **HTTP/JSON contracts**.

---

# Slide 4: Service Implementation: The Aggregator Pattern (`productpage.py`)
**Layout**: 2 Columns (Aggregator Theory on Left | Python Async Source Code on Right)
**Visual**: Fan-out diagram showing productpage initiating asynchronous calls to details and reviews.

- **Role of the Aggregator Microservice**:
  - Serves as the Backend-For-Frontend (BFF), orchestrating downstream calls to assemble the unified product view.
- **Production Source Code**:
```python
# Concurrently fetch details and reviews via REST HTTP
def get_book_details(book_id):
    url = f"http://{detailsHostname}:{detailsPort}/details/{book_id}"
    return requests.get(url, headers=getForwardHeaders(request)).json()

def get_book_reviews(book_id):
    url = f"http://{reviewsHostname}:{reviewsPort}/reviews/{book_id}"
    return requests.get(url, headers=getForwardHeaders(request)).json()
```
- Adheres to **12-Factor App (Config)**: Hostnames resolved dynamically via environment variables (`DETAILS_HOSTNAME`, `REVIEWS_HOSTNAME`).

---

# Slide 5: Evolutionary Architecture: The 3 Reviews Revisions (`reviews.java`)
**Layout**: 3-Row Comparison Table of reviews revisions (v1, v2, v3)
**Visual**: Three visual UI states: Plain text without stars (v1), Black stars (v2), Red stars (v3).

| Reviews Revision | Outbound Network Calls | Rendered User Interface | Production Intent |
|---|---|---|---|
| **`reviews:v1`** | **No** outbound calls to `ratings` | Plain text commentary, **zero stars** | Stable baseline; lowest latency and compute footprint |
| **`reviews:v2`** | Calls `http://ratings:9080` | Comments accompanied by **Black Stars** | Candidate feature release for internal QA testing |
| **`reviews:v3`** | Calls `http://ratings:9080` | Comments accompanied by **Red Stars** | Final production-ready commercial user experience |

- **Unified Codebase (`LibertyRestEndpoint.java`)**: Java Open Liberty endpoint dynamically branches behavior based on the `ratings_service` flag without requiring code changes.

---

# Slide 6: Distributed Tracing & Header Propagation
**Layout**: 2 Columns (Why Header Forwarding is Critical | `getForwardHeaders` Python Code)
**Visual**: Trace context (`x-request-id`, `end-user`) traveling intact across the distributed call chain.

- **The Distributed Context Challenge**:
  - Proxies handle wire telemetry, but applications must **actively propagate specific HTTP headers** to prevent broken trace graphs!
- **Production Code: `getForwardHeaders(request)` in `productpage.py`**:
```python
def getForwardHeaders(request):
    headers = {}
    # 1. Forward Distributed Trace Context (OpenTelemetry / B3 Zipkin)
    ctx = propagator.extract(carrier={k.lower(): v for k, v in request.headers})
    propagator.inject(headers, ctx)
    # 2. Forward user identity header for Istio Layer 7 Canary Routing
    if 'user' in session:
        headers['end-user'] = session['user']
    # 3. Forward x-request-id to correlate logs across all downstream Pods
    if 'x-request-id' in request.headers:
        headers['x-request-id'] = request.headers['x-request-id']
    return headers
```

---

# Slide 7: Why Service Mesh? The Istio Two-Tier Architecture
**Layout**: 2-Tier Architectural Diagram communicating over gRPC xDS APIs
**Visual**: Control Plane `istiod` dynamically streaming xDS configurations down to Envoy Sidecars embedded inside application Pods.

- **The Need for a Dedicated Mesh Layer**:
  - Hardcoding retry, timeout, routing, and mTLS logic into 4 different programming languages creates unmanageable technical debt.
- **1. Control Plane (`istiod` - The Brain)**:
  - Ingests declarative YAML manifests; translates policies into **Envoy xDS gRPC APIs** and delivers certificates via Citadel CA.
- **2. Data Plane (Envoy Sidecars - The Muscle)**:
  - High-performance C++ proxy injected into every Pod via Kubernetes Webhook.
  - Linux `iptables` rules divert **all Inbound traffic to port 15006** and **all Outbound traffic to port 15001** transparently!

---

# Slide 8: Istio Layer 7 Traffic Management: Canary Routing for User `jason`
**Layout**: 2 Columns (Canary Logic Workflow on Left | VirtualService Manifest on Right)
**Visual**: Standard visitors routed to reviews-v1 (no stars); user jason routed to reviews-v2 (black stars).

- **Core Routing Abstractions (CRDs)**:
  - **Gateway** (`bookinfo-gateway.yaml`): Opens edge port 80 for public access.
  - **DestinationRule** (`destination-rule-all.yaml`): Declares version subsets (v1, v2, v3).
  - **VirtualService** (`virtual-service-reviews-test-v2.yaml`): Evaluates Layer 7 headers.
```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: reviews
spec:
  hosts: [ reviews ]
  http:
  - match:
    - headers:
        end-user: { exact: jason }
      route:
      - destination: { host: reviews, subset: v2 } # QA tester -> v2 Black Stars
  - route:
    - destination: { host: reviews, subset: v1 }   # Everyone else -> v1 No Stars
```

---

# Slide 9: Chaos Engineering & Zero Trust Security
**Layout**: 2 Columns (Fault Injection on Left | Transparent mTLS on Right)
**Visual**: Envoy injecting 7-second latency alongside a cryptographic mTLS tunnel connecting Pods.

- **Fault Injection (Chaos Engineering)**:
  - Inject 7-second delay on `ratings` for user `jason`.
  - Upstream timeout fires gracefully; `reviews` serves fallback text without crashing the `productpage` ➔ **Zero Cascading Failure!**
- **Zero Trust Security with Transparent mTLS**:
  - Never trust the internal network. Every inter-Pod packet is authenticated, authorized, and encrypted.
  - **SPIFFE ID**: Cryptographic workload identity (`spiffe://cluster.local/ns/default/sa/...`).
  - **`PeerAuthentication` STRICT**: Closes plaintext access completely across the cluster.

---

# Slide 10: Architectural Summary & Trade-offs
**Layout**: 2-Column Balance Sheet (Gains vs Costs)
**Visual**: Balance scales weighing Architectural Autonomy against Operational Overhead.

| Architectural Capabilities Achieved | Technical Costs & Trade-offs | Production Mitigation Strategy |
|---|---|---|
| **Polyglot Freedom & SRP**: Optimal runtimes chosen per domain service. | **Network Hop Overhead**: Envoy proxy adds **+1.5ms to 3ms** latency per hop. | Evaluate **Istio Ambient Mesh** (node-level ztunnel architecture). |
| **Zero Code Layer 7 Control**: Canary routing and fault injection via YAML. | **Sidecar Memory Footprint**: Each Envoy proxy consumes **30MB–50MB RAM** per Pod. | Restrict xDS configuration distribution using the `Sidecar` CRD. |
| **Zero Trust Enterprise Security**: Transparent mutual TLS encryption across all Pods. | **Operational Complexity**: Challenging debugging when iptables or xDS drift occurs. | Leverage `istioctl analyze` and Distributed Tracing for rapid diagnosis. |

