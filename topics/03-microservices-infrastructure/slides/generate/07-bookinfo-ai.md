# Presentation Topic: Bookinfo Application Architecture & Verification
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Emerald Green (#10b981) & Dark Navy, Architectural Blueprint

---

# Slide 1: Introduction to the Bookinfo Canonical Benchmark
**Layout**: 2 Columns (Left: What is Bookinfo? | Right: Architectural Experimentation Goals)
**Visual**: Browser screenshot of the Bookinfo online bookstore rendering book descriptions, details, and color-coded star ratings.

- **What is Bookinfo?**:
  - The canonical cloud-native benchmark application created by the Istio and CNCF communities.
  - Simulates an online book catalog: displays product details, publisher information, and customer reviews.
- **Architectural Significance**:
  - **Truly Polyglot**: Implemented across 4 distinct programming languages and web frameworks (Python, Ruby, Java, Node.js).
  - Contains zero proprietary networking or security code; all routing, fault injection, mTLS, and telemetry are handled transparently by Kubernetes, Istio, Prometheus, and Grafana!

---

# Slide 2: Polyglot Microservices Topology
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
- Each microservice maintains an independent lifecycle, encapsulated inside its own Docker container.

---

# Slide 3: Microservice 1: `productpage` (Python / Flask)
**Layout**: 2 Columns (Business Logic Overview on Left | Python Async Fan-out Code on Right)
**Visual**: productpage dispatching concurrent HTTP GET requests to gather downstream payloads before rendering HTML.

- **Source Location**: `src/productpage/productpage.py`
- **Technology Stack**: Python 3.12, Flask Framework, Jinja2 Templates, Bootstrap UI.
- **Core Processing Workflow (Aggregator Pattern)**:
  1. Accepts client HTTP requests at `/productpage`.
  2. Dispatches concurrent asynchronous calls to downstream backends:
     - `http://details:9080/details/0`
     - `http://reviews:9080/reviews/0`
  3. Merges JSON payloads into template context and renders the final HTML page.
  4. Exposes an internal `/metrics` endpoint for Prometheus scraping.

---

# Slide 4: Microservices 2 & 4: `details` (Ruby) & `ratings` (Node.js)
**Layout**: 2 Cards side-by-side (details on Left, ratings on Right)
**Visual**: Logos of Ruby and Node.js accompanied by their JSON payload contracts.

- **1. The `details` Microservice (Ruby / Sinatra)**:
  - **Source**: `src/details/details.rb`
  - **Responsibility**: Serves publication metadata (ISBN-10, author, publisher, page count).
  - **Characteristics**: Completely stateless, ultra-lightweight, sub-5ms response times.
- **2. The `ratings` Microservice (Node.js / Express)**:
  - **Source**: `src/ratings/ratings.js`
  - **Responsibility**: Delivers numerical review scores (1 to 5 stars) per book.
  - **Extensibility**: Reads from local memory by default; easily switches to external MySQL databases via environment variables.

---

# Slide 5: Microservice 3: `reviews` (Java) Across Three Evolutionary Revisions
**Layout**: 3-Row Comparison Table of reviews revisions (v1, v2, v3)
**Visual**: Three visual UI states: Plain text without stars (v1), Black stars (v2), Red stars (v3).

| Reviews Revision | Outbound Network Calls | Rendered User Interface | Production Intent |
|---|---|---|---|
| **`reviews:v1`** | **No** outbound calls to `ratings` | Plain text commentary, **zero stars** | Stable baseline; lowest latency and compute footprint |
| **`reviews:v2`** | Calls `http://ratings:9080` | Comments accompanied by **Black Stars** | Candidate feature release for internal QA testing |
| **`reviews:v3`** | Calls `http://ratings:9080` | Comments accompanied by **Red Stars** | Final production-ready commercial user experience |

- **Technology**: Java 17, IBM Open Liberty, JAX-RS RESTful Web Services (`LibertyRestEndpoint.java`).

---

# Slide 6: Distributed Context & Header Propagation
**Layout**: 2 Columns (Why Header Forwarding is Critical | `getForwardHeaders` Python Code)
**Visual**: Trace context (`x-request-id`, `end-user`) traveling intact across the distributed call chain.

- **The Distributed Tracing Challenge**:
  - Envoy proxies handle network recording, but application code must **actively forward specific incoming HTTP headers** to maintain trace continuity!
- **Code Walkthrough: `getForwardHeaders(request)` in `productpage.py`**:
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

# Slide 7: Kubernetes Production Deployment (`platform/kube/bookinfo.yaml`)
**Layout**: 2 Columns (Manifest Structure on Left | `kubectl get pods` Output on Right)
**Visual**: Terminal output showing 6 Pods running in healthy `2/2 Ready` status (App + Envoy).

- **Declared Workload Resources**:
  - **4 Kubernetes Services**: `productpage`, `details`, `reviews`, `ratings` (all listening on internal port 9080).
  - **6 Kubernetes Deployments**:
    - `details-v1` (1 replica), `ratings-v1` (1 replica), `productpage-v1` (1 replica).
    - `reviews-v1`, `reviews-v2`, `reviews-v3` (running concurrently in the same namespace).
- **Cluster Runtime State Verification**:
```text
NAME                              READY   STATUS    RESTARTS   AGE
details-v1-65cfcf56f9-m7pzw       2/2     Running   0          5h
productpage-v1-d5789fdfb-k8x5n    2/2     Running   0          5h
ratings-v1-7c9948f57b-9wpl4       2/2     Running   0          5h
reviews-v1-7598cc9867-q2j5d       2/2     Running   0          5h
reviews-v2-5b667bcbf8-6dptx       2/2     Running   0          5h
reviews-v3-84779c7bbc-xghzt       2/2     Running   0          5h
```

---

# Slide 8: Istio Layer 7 Traffic Routing Integration
**Layout**: 3-Step Configuration Pipeline Diagram
**Visual**: Ingress Gateway ➔ DestinationRule subset definitions ➔ VirtualService routing rules.

- **Step 1: Cluster Edge Admission (`bookinfo-gateway.yaml`)**:
  - Binds port 80 at the Ingress Gateway, exposing the `/productpage` URI to the public internet.
- **Step 2: Defining Subsets (`destination-rule-all.yaml`)**:
  - Maps Kubernetes Pod labels to distinct Istio subsets: `subset: v1`, `subset: v2`, `subset: v3`.
- **Step 3: Intelligent Layer 7 Routing (`virtual-service-reviews-test-v2.yaml`)**:
  - Anonymous visitors: 100% routed to `reviews:v1` (No stars).
  - Authenticated session with header `end-user: jason`: Dynamically routed to `reviews:v2` (Black Stars).
  - **Zero code changes or pod restarts required!**

---

# Slide 9: Four-Step Live Demonstration & Fault Tolerance Verification
**Layout**: 4 Sequenced Action Cards
**Visual**: Step-by-step progression: Automated Setup ➔ Baseline ➔ User Jason Canary ➔ Chaos Delay.

- **Step 1: Automated Infrastructure Bootstrapping (`.\setup-and-run.ps1`)**:
  - Deploys Bookinfo, injects Envoy sidecars, provisions gateways, and verifies 2/2 ready status.
- **Step 2: Baseline Verification (Round-Robin)**:
  - Open `http://localhost/productpage`. Refreshing alternates reviews between v1, v2, and v3.
- **Step 3: Canary Release for QA User `jason`**:
  - Apply VirtualService ➔ Log in as user `jason` ➔ Exclusively renders **Black Stars (v2)**.
  - Log out ➔ Instantly reverts to **No Stars (v1)**.
- **Step 4: Fault Tolerance Verification (Fault Injection)**:
  - Inject 7s latency into `ratings` ➔ Page loads smoothly with reviews fallback ➔ **No cascading crash!**

---

# Slide 10: Architectural Retrospective: Monolith vs Bookinfo
**Layout**: Comprehensive 2-Column Comparison Table
**Visual**: Architectural balance matrix evaluating technology autonomy against operational governance.

| Architectural Dimension | Traditional Monolithic Architecture | Bookinfo Microservices Architecture |
|---|---|---|
| **Technology Strategy** | Enforced single programming language and runtime framework | **Polyglot Flexibility**: Optimal runtime chosen per service domain |
| **Deployment Autonomy** | High-risk redeployment of the entire monolithic binary | **Complete Independence**: Upgrade reviews from v1 to v3 with zero downtime |
| **Operational Overhead** | Low (Single CI/CD pipeline, single host process) | **High**: Demands Kubernetes orchestration and Istio service mesh |
| **Blast Radius Containment** | A single memory leak can bring down the entire business | **Fault Isolation**: Total ratings failure does not crash the core book catalog |
