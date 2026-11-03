# Presentation Topic: Microservices Architecture & Polyglot Systems
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Cloud-Native Engineering, Cyan & Indigo Accents

---

# Slide 1: The Monolith Crisis & The Drive Toward Microservices
**Layout**: 2 Columns (Left: Monolith Bottlenecks | Right: Cloud-Native Paradigm Shift)
**Visual**: A massive cracked stone monolith contrasting with agile, interconnected modular microservices communicating via APIs.

- **Pain Points of Legacy Monolithic Architectures**:
  - **Bloated Codebase**: Exponentially growing compile times, testing bottlenecks, and high cognitive overhead for developers.
  - **Technology Lock-in**: Entire enterprise constrained to a single programming language and runtime framework version.
  - **Brittle Deployment**: A minor bug in an auxiliary module risks cascading failures and brings down the entire system (Single Point of Failure).
  - **Inefficient Scaling**: Forcing horizontal replication of the entire giant application just to satisfy demand on one hot endpoint.
- **The Microservices Mandate**:
  - Decompose large domains into discrete, independently deployable services around **Bounded Contexts**.
  - Establish autonomous cross-functional teams with end-to-end ownership.

---

# Slide 2: Architectural Models Comparison: Monolith vs Modular Monolith vs Microservices
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

# Slide 3: Domain Decomposition via Domain-Driven Design (DDD)
**Layout**: 3 Feature Cards
**Visual**: High-level Domain Map partitioning an e-commerce platform into distinct Bounded Contexts.

- **The Single Responsibility Principle (SRP)**:
  - Each microservice is strictly responsible for a single business capability and encapsulates its domain model.
- **Practical Mapping in the Bookinfo System**:
  - **Catalog Domain** ➔ `details`: Exclusively manages book metadata (ISBN, author, publisher, page count).
  - **Feedback Domain** ➔ `reviews`: Owns reader textual feedback and overall commentary.
  - **Scoring Domain** ➔ `ratings`: Manages numerical scores (1 to 5 stars) and persistent star tallies.
  - **Aggregation Domain** ➔ `productpage`: Serves as the web entry point and presentation layer.

---

# Slide 4: Polyglot Microservices: Choosing the Right Tool for the Job
**Layout**: 4 Cards showcasing the 4 distinct languages in the Bookinfo Architecture
**Visual**: Logos of Python, Ruby, Java, and Node.js connected through standard REST HTTP contracts.

- **Python (Flask)** — `productpage`:
  - Rapid UI development, rich Jinja2 template rendering, dynamic API aggregation.
- **Ruby (Sinatra)** — `details`:
  - Minimalist REST service, lightning-fast boot time, ultralight memory footprint for static metadata.
- **Java (Open Liberty / JAX-RS)** — `reviews`:
  - Enterprise-grade concurrent request handling, robust multithreading, and strict type safety.
- **Node.js (Express)** — `ratings`:
  - Event-driven, non-blocking asynchronous I/O ideal for rapid scoring and database queries.
- **Key Architectural Rule**: Services share zero internal libraries; inter-service communication is governed strictly by **HTTP/JSON contracts**.

---

# Slide 5: Code Analysis: The Aggregator Pattern (`productpage.py`)
**Layout**: 2 Columns (Left: Aggregator Pattern Theory | Right: Python Source Code)
**Visual**: Fan-out diagram showing productpage initiating asynchronous calls to details and reviews.

- **Role of the Aggregator Service**:
  - Acts as an internal API Gateway / Backend-For-Frontend (BFF), fetching distributed payloads to construct a unified view.
- **Production Source Code**:
```python
# Concurrently query details and reviews microservices via HTTP REST
def get_book_details(book_id):
    url = f"http://{detailsHostname}:{detailsPort}/details/{book_id}"
    return requests.get(url, headers=getForwardHeaders(request)).json()

def get_book_reviews(book_id):
    url = f"http://{reviewsHostname}:{reviewsPort}/reviews/{book_id}"
    return requests.get(url, headers=getForwardHeaders(request)).json()
```
- Employs **12-Factor App** design: service endpoints dynamically resolved via environment variables (`DETAILS_HOSTNAME`, `REVIEWS_HOSTNAME`).

---

# Slide 6: Code Analysis: Evolutionary Design in Java (`LibertyRestEndpoint.java`)
**Layout**: 2 Columns (Left: Evolutionary Architecture Principles | Right: Java JAX-RS Source Code)
**Visual**: Execution branching logic showing v1 (plain text), v2 (black stars), and v3 (red stars).

- **Supporting Multiple Revisions in a Unified Codebase**:
  - Dynamic behavior toggling via environment variables (`ENABLE_RATINGS`) without breaking upstream consumers.
- **Production Source Code**:
```java
@GET
@Path("/reviews/{productId}")
@Produces(MediaType.APPLICATION_JSON)
public Response bookReviewsById(@PathParam("productId") int productId) {
    JsonObjectBuilder json = Json.createObjectBuilder();
    // Dynamically query auxiliary ratings service based on environment flag
    if (ratings_service) {
        JsonObject ratingsResponse = getRatings(productId);
        json.add("ratings", ratingsResponse); // v2 (Black Stars) or v3 (Red Stars)
    }
    // If ratings_service is disabled: Return v1 baseline text without star ratings
    return Response.ok(json.build()).build();
}
```

---

# Slide 7: Inter-Service Communication & API Contracts
**Layout**: 2 Columns (Synchronous vs Asynchronous Communication)
**Visual**: Direct REST call sequence diagram contrasted with an Event Bus message broker pipeline.

- **Synchronous Communication (REST / gRPC)**:
  - Immediate request-response model, intuitive debugging, low initial complexity.
  - Risk: Tight temporal coupling and downstream cascading latency if downstream services stall.
- **Asynchronous Communication (Kafka / RabbitMQ / CloudEvents)**:
  - Event-driven decoupling; producer publishes events without caring about subscriber processing time.
  - Crucial for order fulfillment, background notifications, and inventory updates.
- **Strict API Contracts**:
  - Enforce schema contracts (OpenAPI / Protobuf) to guarantee backward and forward compatibility.

---

# Slide 8: Distributed Data Management: The Database-per-Service Principle
**Layout**: Architectural Diagram + ACID vs BASE Comparison Table
**Visual**: Independent databases per service communicating through domain events and Saga workflows.

- **The Non-Negotiable Rule**:
  - Direct cross-service database access is strictly prohibited. Service A must never execute queries against Service B's database.
- **Trading ACID for BASE**:
  - Distributed Two-Phase Commit (2PC) transactions introduce severe locking and latency.
  - Microservices embrace **BASE** (Basically Available, Soft-state, Eventual Consistency).
  - Implement the **Saga Pattern** with compensating actions to maintain transactional consistency across distributed boundaries.

---

# Slide 9: System Resilience & Preventing Cascading Failures
**Layout**: 3 Feature Cards
**Visual**: Circuit Breaker state machine transitioning from Closed ➔ Open ➔ Half-Open.

- **1. Circuit Breaker Pattern**:
  - Automatically trips open when downstream failure thresholds are breached, returning fast fallbacks instead of hanging threads.
- **2. Rate Limiting & Shedding**:
  - Prevents noisy neighbors or rogue traffic bursts from exhausting shared cluster threadpools.
- **3. Graceful Degradation in Bookinfo**:
  - When `ratings` experiences total failure, `productpage` continues rendering book descriptions and written reviews without crashing!

---

# Slide 10: Architectural Summary & Trade-offs
**Layout**: 2-Column Balance Sheet (Architectural Gains vs Operational Costs)
**Visual**: Balance scale weighing Team Autonomy against Operational Complexity.

| Architectural Benefits | Inherent Operational Challenges | Mandatory Technical Solutions |
|---|---|---|
| **Polyglot Freedom**: Optimal runtime chosen per service domain. | **Ecosystem Fragmentation**: Complex dependency management and inconsistent runtimes. | Standardize builds using **Docker Containers**. |
| **Independent Scaling**: Scale only congested endpoints efficiently. | **Distributed Networking**: Ephemeral IPs, service discovery, and routing failures. | Implement **Kubernetes Orchestration**. |
| **Contained Blast Radius**: Failure isolated to local microservice boundaries. | **Loss of End-to-End Visibility**: Difficult debugging across distributed hops. | Deploy **Istio Mesh & Distributed Tracing**. |
