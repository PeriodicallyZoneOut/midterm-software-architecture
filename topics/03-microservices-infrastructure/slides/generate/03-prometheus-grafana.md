# Master Deck 3: Cloud-Native Observability with Prometheus & Grafana
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Prometheus Flame (#e6522c) & Grafana Orange (#f46800), SRE Cockpit

---

# Slide 1: The Observability Imperative: Why Metrics are the SRE Foundation
**Layout**: 3 Columns representing the 3 Pillars of Observability (Logs, Traces, Metrics)
**Visual**: Venn diagram of Logs, Metrics, and Traces highlighting the low-overhead, real-time alertability of Metrics.

- **The Three Pillars of Cloud-Native Observability**:
  - **1. Logs**: Rich chronological event details (High storage cost, slow to query across terabytes of data).
  - **2. Traces**: Request lifecycles across distributed microservice boundaries (Vital for debugging, but sampled).
  - **3. Metrics**: Compact numeric time-series data aggregated at regular intervals (Near-zero cost, instant alerting).
- **The Prometheus & Grafana Synergy**:
  - Prometheus acts as the high-throughput **Time-Series Engine (TSDB)** collecting and evaluating metrics.
  - Grafana acts as the unified **Visualization Command Center**, translating raw vectors into actionable SRE dashboards.

---

# Slide 2: Prometheus Server Architectural Topology
**Layout**: System Architecture Diagram showing data flow from Targets into TSDB and out to APIs
**Visual**: Endpoints being scraped via HTTP, written to local TSDB, and queried by Grafana via the PromQL engine.

- **Core Server Architectural Components**:
  - **Retrieval / Scrape Manager**: Dispatches periodic HTTP GET requests to scrape metrics from target endpoints.
  - **Time-Series Database (TSDB)**: High-throughput local storage engine appending millions of data points per second directly to disk.
  - **PromQL Engine**: Evaluates functional algebraic queries, computing rates, moving averages, and quantiles.
  - **Kubernetes Service Discovery**: Dynamically discovers newly scheduled Pods via API Server watches.

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

# Slide 4: Multi-Dimensional Data Model & 4 Metric Types
**Layout**: Syntax breakdown of a Metric Record + 4 Feature Cards for Metric Types
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
- **1. Counter**: Monotonically increasing; paired with `rate()` for throughput (`istio_requests_total`).
- **2. Gauge**: Instantaneous snapshot value; can rise or fall arbitrarily (`container_memory_usage_bytes`).
- **3. Histogram**: Bins observations into cumulative buckets (`_bucket{le="..."}`) for percentiles.
- **4. Summary**: Pre-computed client-side quantiles (less suitable for distributed aggregation).

---

# Slide 5: PromQL in Action: Measuring Golden Signals
**Layout**: 3 Horizontal Formula Callout Cards (Throughput, Latency, Error Ratios)
**Visual**: Formula breakdowns with real-world query outputs from the Bookinfo cluster.

- **1. Requests Per Second (Throughput)**:
```promql
sum(rate(istio_requests_total{reporter="destination"}[1m])) by (destination_workload)
```
- **2. Tail Latency 95th Percentile (User Experience)**:
```promql
histogram_quantile(
  0.95,
  sum(rate(istio_request_duration_milliseconds_bucket{destination_workload="productpage-v1"}[1m])) by (le)
)
```
- **3. Error Rate Ratio (SLO Compliance)**:
```promql
(sum(rate(istio_requests_total{reporter="destination", response_code=~"5.*"}[5m]))
 / sum(rate(istio_requests_total{reporter="destination"}[5m]))) * 100
```

---

# Slide 6: Grafana: The SRE Single Pane of Glass
**Layout**: 2 Columns (Left: Cognitive Overload of Raw PromQL | Right: The Power of Visual SRE Dashboards)
**Visual**: Raw CLI terminal scrolling text contrasted with an elegant, multi-panel Grafana command center.

- **The Need for Human-Centric Visualization**:
  - During live production incidents, engineers cannot waste critical minutes typing complex PromQL syntax.
  - Grafana acts as the unified **Single Pane of Glass**, exposing SLO breaches through intuitive color-coded thresholds.
- **Config-as-Code Provisioning (`samples/addons/grafana.yaml`)**:
```yaml
datasources.yaml: |
  apiVersion: 1
  datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    jsonData:
      timeInterval: 15s
```
- Fully automated: ConfigMaps mount data sources and pre-packaged Istio dashboards at pod startup.

---

# Slide 7: Visualization Panels & The Istio Mesh Dashboard
**Layout**: High-Level Overview Mockup of the Istio Mesh Dashboard
**Visual**: Top row of global KPI cards (Volume, Success Rate, 4xx/5xx Errors) above a visual topology flow.

- **Diverse Panel Ecosystem**:
  - **Stat Panel**: Large numeric callout for critical SLAs (`Current RPS: 48.2`).
  - **Gauge Panel**: Visual dial measuring resource saturation with red alert zones.
  - **Time-Series Panel**: Overlays multi-percentile latency curves (P50, P90, P99).
- **Macro-Level Istio Mesh Dashboard**:
  - **Global Request Volume**: Aggregates all incoming traffic entering through Ingress Gateways.
  - **Global Success Rate**: System-wide health score (Target: `> 99.9%`).
  - **4xx / 5xx Breakdown**: Immediate attribution of client vs server errors across services.

---

# Slide 8: Istio Service Dashboard & Cross-Layer Correlation
**Layout**: 2 Horizontal Panels stacked vertically (Top: Istio Network Telemetry | Bottom: Node CPU/RAM)
**Visual**: Traffic burst to 50 req/s on the top graph perfectly aligning with container CPU spiking from 15% to 92% below.

- **Granular Service Deep-Dive**:
  - Tracks inbound calls to `reviews` (from `productpage`) and outbound calls (to `ratings`).
  - Simultaneously overlays P50, P90, and P99 latency percentiles to detect tail-end degradation.
- **Multi-Source Cross-Layer Correlation**:
  - **Top Graph (Network Telemetry)**: Shows RPS surging from 10 to 50 req/s, causing latency to spike to 280ms.
  - **Bottom Graph (cAdvisor Metrics)**: Shows container CPU utilization simultaneously hitting the 100% CPU limit!
  - ➔ **Root Cause Proved**: Latency is driven by container CPU starvation, not network latency.

---

# Slide 9: Dashboard Templating via Dynamic Variables & SRE Alerting
**Layout**: 2 Columns (Dynamic Variables Dropdown on Left | Alert Webhook Flow on Right)
**Visual**: Selecting the "reviews" dropdown instantly re-renders all 10 dashboard panels + Slack alert notification card.

- **Dynamic Dashboard Templating**:
```sql
# Dynamically queries available services from Prometheus labels
label_values(istio_requests_total{destination_workload_namespace="$namespace"}, destination_service_name)
```
  - A **single template dashboard** dynamically adapts to any selected service across the entire cluster!
- **SRE Alerting Pipeline**:
  - Evaluates if `Error Rate > 1%` or `P95 Latency > 500ms`.
  - Dispatches automated alert webhooks to **Slack / PagerDuty** with embedded chart snapshots and direct dashboard deep-links.

---

# Slide 10: Observability Architectural Trade-offs & Production SRE
**Layout**: 2-Column Balance Sheet (Observability Power vs Infrastructure Costs)
**Visual**: Balance scales weighing Real-Time Telemetry against Prometheus Ingestion Overhead.

| Observability Capabilities Achieved | Technical Costs & Trade-offs | Production Best Practices |
|---|---|---|
| **Multi-Dimensional Query Power**: Blazing-fast aggregations across dynamic labels via PromQL. | **Cardinality Explosion Risk**: High-cardinality labels exhaust server memory rapidly. | Strictly forbid injecting User IDs, IP addresses, or UUIDs into Prometheus labels. |
| **Enterprise SRE Visualization**: Turns raw data into compelling operational insights for all stakeholders. | **Prometheus Query Saturation**: Too many open dashboards running short refresh intervals can saturate TSDB CPU. | Enforce sensible default auto-refresh intervals (`Auto-refresh: 30s` or `1m`). |
| **Declarative Dashboard-as-Code**: Version-controlled, portable JSON definitions. | **Configuration Drift**: Manual UI tweaks are wiped out when ephemeral pods restart. | Export dashboard JSON files and manage them via Git and Kubernetes ConfigMaps! |

