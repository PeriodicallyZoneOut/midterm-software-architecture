# Presentation Topic: Data Visualization & SRE Dashboards with Grafana
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Grafana Orange (#f46800) & Midnight Black, SRE Dashboard Aesthetic

---

# Slide 1: Bridging Raw Metrics & Human Intuition in SRE
**Layout**: 2 Columns (Left: Cognitive Overload of Raw PromQL | Right: The Power of Visual SRE Dashboards)
**Visual**: Raw CLI terminal scrolling text contrasted with an elegant, multi-panel Grafana command center.

- **The Gap Between Raw Time Series & Human Decision-Making**:
  - Prometheus records millions of precise time series samples across distributed nodes.
  - But during high-severity production incidents, on-call engineers cannot waste critical minutes typing complex PromQL queries from memory!
- **Grafana's Core Mission**:
  - Acts as the definitive **Single Pane of Glass** uniting metrics, logs, and traces.
  - Instantly exposes SLO breaches through intuitive color-coded thresholds: **Green (Healthy) ➔ Yellow (Warning) ➔ Red (Critical)**.
  - Transforms abstract mathematical vectors into dynamic trendlines, accelerating Mean Time To Resolution (MTTR).

---

# Slide 2: Grafana Architecture & Automated DataSource Provisioning
**Layout**: Architectural Flow Diagram (Grafana Engine ➔ HTTP Proxy ➔ Prometheus TSDB)
**Visual**: Secure internal communication channel inside the `istio-system` namespace querying Prometheus on port 9090.

- **Grafana Architecture Fundamentals**:
  - Operates as a stateless visualization engine, dispatching backend queries to Prometheus via an authenticated HTTP proxy.
- **Config-as-Code Automation (`samples/addons/grafana.yaml`)**:
  - Eliminates brittle manual UI configuration through automated provisioning:
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
- Upon pod startup, Kubernetes ConfigMaps automatically mount data sources and pre-configured Istio dashboards with zero manual intervention.

---

# Slide 3: Diverse Panel Ecosystem & SRE Visualization Principles
**Layout**: 2x2 Grid displaying the 4 essential panel types
**Visual**: Graphical mockup of Stat Panel (large numbers), Gauge (semi-circle), Time-Series (wave graphs), and Bar Chart.

- **1. Stat Panel (Instantaneous Key Indicators)**:
  - Emphasizes single critical metrics with high readability (e.g., `Current RPS: 48.2`).
- **2. Gauge Panel (Resource Saturation)**:
  - Tracks resource usage against hard operational limits, transitioning to red when crossing 80% saturation.
- **3. Time-Series Panel (Longitudinal Trends)**:
  - Simultaneously overlays multi-percentile latency distributions (P50, P90, P99) over 1-hour windows.
- **4. Bar / Distribution Charts (Status Code Ratios)**:
  - Visualizes response code distributions (e.g., 98.2% 200 OK vs 1.8% 503 Service Unavailable).

---

# Slide 4: Istio Mesh Dashboard: Cluster-Wide Global Telemetry
**Layout**: High-Level Overview Mockup of the Istio Mesh Dashboard
**Visual**: Top row of global KPI cards (Volume, Success Rate, 4xx/5xx Errors) above a visual topology flow.

- **Macro-Level Executive Overview**:
  - **Global Request Volume**: Aggregates all incoming traffic entering through edge Ingress Gateways (e.g., `48.2 req/s`).
  - **Global Success Rate**: System-wide health score (Target: `> 99.9%`).
  - **4xx / 5xx Error Breakdown**: Immediate attribution of client vs server errors across services.
- **Value for Engineering Leadership (VP / CTO)**:
  - Delivers a 3-second snapshot confirming whether the entire Bookinfo ecosystem is healthy or experiencing degradation.

---

# Slide 5: Istio Service Dashboard: Microservice Deep-Dive
**Layout**: 2 Columns (Inbound / Outbound Request Flow | Latency Percentiles P50/P90/P99)
**Visual**: Traffic graph for the `reviews` service showing incoming calls from `productpage` and downstream calls to `ratings`.

- **Granular Workload Telemetry (Deep-Dive Analysis)**:
  - **Inbound Request Volume**: Identifies callers (e.g., 100% of incoming traffic originates from `productpage-v1`).
  - **Outbound Request Volume**: Tracks downstream dependencies (e.g., `reviews-v2` invoking `ratings-v1`).
  - **Request Duration Percentiles**: Simultaneously tracks three distinct percentiles:
    - **P50 (Median)**: General user experience baseline (~25ms).
    - **P99**: Pinpoints intermittent tail latency spikes when downstream calls stall!

---

# Slide 6: Cross-Layer Correlation: Infrastructure vs Network Telemetry
**Layout**: 2 Horizontal Panels stacked vertically (Top: Istio Network Telemetry | Bottom: Node CPU/RAM)
**Visual**: Traffic burst to 50 req/s on the top graph perfectly aligning with container CPU spiking from 15% to 92% below.

- **Multi-Source Telemetry Correlation**:
  - Addresses the classic troubleshooting mystery: *Is latency spiking due to application CPU starvation or network congestion?*
- **The Value of Side-by-Side Panel Placement**:
  - **Top Panel (Istio Telemetry)**: Shows RPS surging from 10 to 50 req/s, causing latency to jump from 35ms to 280ms.
  - **Bottom Panel (cAdvisor Metrics)**: Shows container CPU utilization simultaneously maxing out against the 100% CPU limit!
  - ➔ **Instant Actionable Diagnosis**: Increase `resources.limits.cpu` or configure a **Horizontal Pod Autoscaler (HPA)**.

---

# Slide 7: Dashboard Templating via Dynamic Variables
**Layout**: Dropdown Filter Bar Illustration: [$namespace] [$service] [$workload]
**Visual**: Selecting the "reviews" dropdown instantly re-renders all 10 dashboard panels with review-specific telemetry.

- **The Problem with Static Dashboards**:
  - Managing 30 microservices would require authoring and maintaining 30 separate dashboard JSON definitions!
  - Inefficient, error-prone, and impossible to maintain across evolving teams.
- **Grafana's Dynamic Variable Solution**:
```sql
# Dynamically queries available services from Prometheus labels
label_values(istio_requests_total{destination_workload_namespace="$namespace"}, destination_service_name)
```
- A **single template dashboard** dynamically adapts to any selected service, injecting variable values directly into underlying PromQL queries!

---

# Slide 8: Real-Time Verification: Load Test Telemetry Burst
**Layout**: Load Test Script Callout + Real-World Telemetry Reaction Curves
**Visual**: Rectangular step-function surge in RPS accompanied by rock-solid latency curves.

- **Load Injection Verification Script**:
```powershell
for ($i=1; $i -le 100; $i++) {
    Invoke-WebRequest -Uri "http://localhost/productpage" -UseBasicParsing | Out-Null
}
```
- **Real-Time Dashboard Observations**:
  1. **RPS Panel**: Instantly jumps from an idle 0.2 to **28.5 requests/sec**.
  2. **Latency P95 Panel**: Remains completely stable at **45ms**, with zero abnormal spikes.
  3. **Success Rate Panel**: Maintains a flawless **100%**, confirming zero dropped packets.

---

# Slide 9: SRE Alerting Rules & Proactive SLO Management
**Layout**: 2 Columns (Alert Rule Definition on Left | Slack Notification Payload on Right)
**Visual**: Trendline crossing a red threshold line, triggering an automated alert webhook containing dashboard deep-links.

- **Transitioning from Reactive to Proactive Operations**:
  - Engineers cannot manually monitor dashboards 24/7.
  - Grafana evaluates alert rules directly against visualization query data.
- **Production SRE Alerting Pipeline**:
  1. **Condition**: Evaluates if `Error Rate > 1%` or `P95 Latency > 500ms`.
  2. **Evaluation Window**: Runs every 1 minute; transitions to `Firing` if condition persists for 5 consecutive minutes (`for: 5m`).
  3. **Notification Routing**: Dispatches rich webhooks to **Slack / PagerDuty** with embedded chart snapshots and direct dashboard URLs!

---

# Slide 10: Grafana Architectural Evaluation & Trade-offs
**Layout**: 2-Column Balance Sheet (Observability Power vs Infrastructure Costs)
**Visual**: Dashboard-as-Code repository storing JSON manifests under version control.

| Core Observability Strengths | Operational Costs & Challenges | Best Practice Mitigation |
|---|---|---|
| **Enterprise Visualization**: Turns raw data into compelling operational insights for all stakeholders. | **Prometheus Query Load**: Too many open dashboards running short refresh intervals can saturate TSDB CPU. | Enforce sensible default auto-refresh intervals (`Auto-refresh: 30s` or `1m`). |
| **Dynamic Templating**: A single dashboard scales effortlessly to monitor hundreds of microservices. | **Client Browser Overhead**: Dashboards with dozens of heavy panels can freeze client web browsers. | Partition views into dedicated Mesh, Service, and Host-level dashboards. |
| **Dashboard-as-Code Philosophy**: Dashboards are version-controlled, portable JSON definitions. | **Configuration Drift**: Manual UI tweaks are wiped out when ephemeral pods restart. | Export dashboard JSON files and manage them via Git and Kubernetes ConfigMaps! |
