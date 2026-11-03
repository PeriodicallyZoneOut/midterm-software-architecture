# Presentation Topic: System Monitoring & Metrics with Prometheus
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Prometheus Orange (#e6522c) & Deep Graphite, High Visibility

---

# Slide 1: The Metrics Pillar & Observability Foundations
**Layout**: 3 Columns representing the 3 Pillars of Observability (Logs, Traces, Metrics)
**Visual**: Venn diagram of Logs, Metrics, and Traces highlighting the low-overhead, real-time alertability of Metrics.

- **The Three Pillars of Cloud-Native Observability**:
  - **1. Logs**: Rich, contextual chronological event records (high context, expensive to store and index at scale).
  - **2. Traces**: End-to-end distributed transaction tracking across complex service boundaries.
  - **3. Metrics**: Compact, numerically aggregated time-series data (ultra-low storage overhead, instant alerting).
- **The Prometheus Industry Standard**:
  - The second project to graduate from the **Cloud Native Computing Foundation (CNCF)** after Kubernetes.
  - The foundational de facto standard for systems telemetry across modern cloud-native architectures.

---

# Slide 2: Prometheus Server Architectural Topology
**Layout**: System Architecture Diagram showing data flow from Targets into TSDB and out to APIs
**Visual**: Endpoints being scraped via HTTP, written to local TSDB, and queried by Grafana via the PromQL engine.

- **Core Server Components**:
  - **Retrieval / Scrape Manager**: Dispatches periodic HTTP GET requests to scrape metrics from target endpoints.
  - **Time-Series Database (TSDB)**: High-throughput local storage engine optimized for appending millions of data points per second.
  - **PromQL Engine**: Evaluates functional algebraic queries, calculating rates, ratios, and percentiles.
  - **Kubernetes Service Discovery**: Dynamically registers newly scheduled Pods, eliminating static endpoint configurations.

---

# Slide 3: The Pull Model & Scraping Envoy Sidecars (`:15090`)
**Layout**: 2 Columns (Push vs Pull Paradigm | Envoy Scraping Configuration in Bookinfo)
**Visual**: Prometheus Server pulling metrics every 15s from Envoy's internal admin port :15090.

- **Why Prometheus Chooses the Pull Model Over Push**:
  - *Push Model*: Thousands of failing microservices pushing data simultaneously will DDoS the monitoring cluster during major outages!
  - *Pull Model (Prometheus)*: Central server regulates its own ingestion rate; immediately identifies target downtime when a scrape fails.
- **Scraping Envoy Sidecars in Bookinfo (`samples/addons/prometheus.yaml`)**:
  - Application code (Python/Java) requires zero metric instrumentation.
  - Envoy proxies automatically record Layer 7 golden signals and expose them on `:15090/stats/prometheus`.
  - Prometheus discovers Pods via Kubernetes annotations and collects telemetry every 15 seconds.

---

# Slide 4: Multi-Dimensional Time-Series Data Model
**Layout**: Syntax breakdown of a Prometheus Metric Record
**Visual**: Callout diagram dissecting Metric Name, Key-Value Labels, 64-bit Float Value, and Timestamp.

$$\text{<metric\_name>}\{\text{<label\_key>} = \text{"<label\_value>"}, ...\} \quad \text{float64\_value} \quad [\text{timestamp}]$$

```text
istio_requests_total{
  reporter="destination",
  source_workload="productpage-v1",
  destination_workload="reviews-v2",
  response_code="200"
} 14285 1741046400000
```
- **The Multi-Dimensional Labeling Advantage**:
  - Empowers engineers to slice and dice telemetry across any axis without changing metric names:
  - Filter by target workload: `destination_workload="reviews-v2"`
  - Filter by error status: `response_code=~"5.*"`
  - Group aggregations: `by (destination_workload)`

---

# Slide 5: The Four Core Metric Types
**Layout**: 4 Feature Cards
**Visual**: Meter icons: Counter (Ascending-only), Gauge (Fluid level), Histogram (Cumulative buckets), Summary.

- **1. Counter (Monotonically Increasing Counter)**:
  - Can only increase or reset to 0 upon process restart. Paired with `rate()` to compute per-second throughput.
  - *Example*: `istio_requests_total` (Cumulative requests processed).
- **2. Gauge (Instantaneous Value Snapshot)**:
  - Can rise and fall arbitrarily; reflects the instantaneous state of a resource.
  - *Example*: `container_memory_usage_bytes` (Active Pod RAM utilization).
- **3. Histogram (Cumulative Distribution Buckets)**:
  - Samples observations into configurable buckets (`_bucket{le="..."}`) for percentile calculations.
  - *Example*: `istio_request_duration_milliseconds_bucket` (Latency percentiles).
- **4. Summary (Client-side Quantile Aggregator)**:
  - Calculates pre-computed quantiles client-side (less suitable for distributed aggregation).

---

# Slide 6: PromQL Query Fundamentals & Vector Evaluation
**Layout**: 2 Columns (Vector Output Types | Core Mathematical Operators)
**Visual**: Instant Vector (single point snapshot) contrasted with Range Vector (time series array).

- **PromQL Vector Types**:
  - **Instant Vector**: A set of time series containing a single value for each series at the evaluation timestamp:
    `istio_requests_total{destination_workload="reviews-v1"}`
  - **Range Vector**: A set of time series containing a buffer of values over a specified time window:
    `istio_requests_total{destination_workload="reviews-v1"}[5m]`
- **Essential PromQL Functions**:
  - `rate(v[range])`: Computes the per-second average rate of increase of a Counter, automatically handling counter resets.
  - `sum() by (...)`: Aggregates and collapses vectors across specified label dimensions.
  - `histogram_quantile(φ, b)`: Calculates the $\phi$-quantile (e.g., 0.95 for P95) from histogram buckets.

---

# Slide 7: PromQL in Action 1: Measuring Traffic & Throughput (RPS)
**Layout**: Large PromQL Formula Callout + Horizontal Bar Chart comparing service throughputs
**Visual**: Throughput breakdown: productpage 32.4 req/s, reviews 23.9 req/s, details 28.5 req/s.

```promql
sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)
```

- **Query Deconstruction**:
  - `reporter="destination"`: Measures requests at the receiving boundary to prevent double-counting across hops.
  - `[1m]`: Uses a 1-minute sliding time window to calculate smooth, noise-free derivatives.
  - `rate(...)`: Converts raw cumulative request totals into **Requests Per Second (RPS)**.
  - `sum(...) by (destination_workload)`: Aggregates across all backing Pod replicas to compute service-wide throughput.

---

# Slide 8: PromQL in Action 2: Tail Latency Percentiles (P95/P99)
**Layout**: 2 Columns (The Danger of Averages | PromQL Percentile Formula)
**Visual**: Bell curve latency distribution showing the dangerous "Long Tail" at the 95th and 99th percentiles.

- **Why Mean Latency is a Dangerous Lie**:
  - Mathematical averages obscure severe tail-end performance degradations.
  - 95% of casual visitors might load a page in 30ms, while 5% of valuable VIP shoppers experience a 5-second hang!
- **PromQL P95 Latency Formula for `productpage`**:
```promql
histogram_quantile(
  0.95,
  sum(rate(istio_request_duration_milliseconds_bucket{destination_workload="productpage-v1"}[1m])) by (le)
)
```
- Envoy bins request durations into cumulative buckets: `le="10"`, `le="50"`, `le="250"`, `le="1000"`. The `histogram_quantile` function performs linear interpolation to pinpoint the exact 95th percentile latency boundary.

---

# Slide 9: PromQL in Action 3: Error Rate Tracking & SLO Enforcement
**Layout**: 2 Columns (5xx Error Rate Ratio Formula | SRE Production Practice)
**Visual**: SRE SLO gauge: Green zone (99.9% success rate), Warning threshold (0.5%), Critical alert boundary (1.0%).

```promql
# Calculate the percentage ratio of HTTP 5xx errors to total incoming traffic
(
  sum(rate(istio_requests_total{reporter="destination", response_code=~"5.*"}[5m]))
  /
  sum(rate(istio_requests_total{reporter="destination"}[5m]))
) * 100
```

- **Production SRE Application**:
  - **Service Level Objective (SLO)**: Formulate the objective: "HTTP error rate must not exceed 1% over any 5-minute sliding window."
  - When the 5xx ratio breaches 1.0%, Prometheus transitions the alert to **Firing** status, notifying on-call engineers before customer impact deepens.

---

# Slide 10: Prometheus Architectural Evaluation & Trade-offs
**Layout**: 2-Column Balance Sheet (Monitoring Superpowers vs Inherent Constraints)
**Visual**: Architectural diagram showing Prometheus forwarding long-term time series to object storage via Thanos.

| Monitoring Strengths | Architectural Constraints & Risks | Production Engineering Solutions |
|---|---|---|
| **Multi-Dimensional Query Speed**: Blazing-fast aggregations across dynamic labels via PromQL. | **Cardinality Explosion Risk**: High-cardinality labels exhaust server memory rapidly. | Strictly forbid injecting User IDs, IP addresses, or UUIDs into Prometheus labels. |
| **Resilient Pull Model**: Predictable ingestion rate; immune to cascading push stampedes. | **Telemetry Resolution Lag**: Telemetry is inherently delayed by the scrape interval (15s). | Balance scrape resolution against CPU and network bandwidth budgets. |
| **Zero External Dependencies**: Operates autonomously with local storage; zero cluster coupling. | **Limited Long-Term Retention**: Embedded TSDB is not designed for multi-year retention. | Integrate **Thanos** or **Cortex** to offload historical metrics to S3/MinIO. |
