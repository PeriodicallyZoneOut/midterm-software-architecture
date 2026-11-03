# Presentation Topic: Container Orchestration with Kubernetes (K8s)
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Kubernetes Blue (#326ce5) & Slate Gray, Enterprise Grade

---

# Slide 1: Production Challenges: The Need for Container Orchestration
**Layout**: 2 Columns (Left: Operational Chaos of Raw Docker | Right: Kubernetes Automation)
**Visual**: Overwhelmed sysadmin managing dozens of fragmented VMs vs Kubernetes reconciling cluster state automatically.

- **What Happens When Systems Grow from 5 to 500 Containers?**:
  - How do you schedule containers onto machines with adequate available CPU and RAM?
  - When an underlying physical server suffers hardware failure, who resurrects the workloads elsewhere?
  - How do services reliably discover each other when container IP addresses fluctuate continuously?
  - How do you roll out zero-downtime updates without dropping inflight user traffic?
- **The Kubernetes (K8s) Breakthrough**:
  - The de facto open-source container orchestration platform originally engineered by Google.
  - Automates scheduling, service discovery, horizontal scaling, and continuous self-healing.

---

# Slide 2: Two-Tier Architecture: Control Plane vs Worker Nodes
**Layout**: 2-Tier Stack Diagram (Brain Tier on top, Execution Tier below)
**Visual**: Control Plane components (API Server, etcd, Scheduler, Controller) dispatching state via Kubelet to Worker Nodes.

- **1. The Control Plane (The Cluster's Brain)**:
  - `kube-apiserver`: The central hub and sole gateway handling all administrative REST commands.
  - `etcd`: Highly available distributed key-value store holding complete cluster desired state.
  - `kube-scheduler`: Analyzes resource availability and node affinities to place incoming Pods.
  - `kube-controller-manager`: Runs reconciliation loops to ensure actual state matches desired state.
- **2. Worker Nodes (The Workload Execution Engine)**:
  - `kubelet`: Node agent ensuring containers declared in PodSpecs are running and healthy.
  - `kube-proxy`: Maintains network rules and implements Layer 4 TCP/UDP load balancing.
  - `Container Runtime`: Low-level engine executing containers (containerd, CRI-O).

---

# Slide 3: The Pod Abstraction & The Multi-Container Sidecar Pattern
**Layout**: 2 Columns (Left: Pod Fundamentals | Right: 2/2 Ready Bookinfo Pod Structure)
**Visual**: A Pod perimeter enclosing two containers sharing a single IP, network namespace, and localhost.

- **What is a Kubernetes Pod?**:
  - The smallest atomic schedulable execution unit in Kubernetes.
  - Encloses one or more tightly coupled containers sharing storage volumes and network namespaces.
  - Containers within a single Pod communicate at near-zero latency over `localhost`.
- **The Bookinfo "2/2 Ready" Sidecar Architecture**:
  - **Container 1**: Core business application (Python `productpage`, Ruby `details`, Java `reviews`).
  - **Container 2**: Infrastructure auxiliary proxy (`istio-proxy` / Envoy).
  - The sidecar acts as an invisible network chaperone handling telemetry, routing, and mTLS.

---

# Slide 4: Declarative Desired State & The Reconciliation Loop
**Layout**: Closed-Loop Control Flow Diagram (Declare ➔ Observe ➔ Diff ➔ Act)
**Visual**: Continuous circular loop showing Kubernetes Controller monitoring and healing divergent state.

- **Imperative vs Declarative Management**:
  - *Imperative*: "Deploy 3 containers on Node A, then bind port 80." (Brittle, unrepeatable).
  - *Declarative (Kubernetes)*: "Maintain exactly 3 healthy replicas of reviews-v1 at all times."
- **The Infinite Reconciliation Loop**:
  1. **Observe**: Continuously reads real-time telemetry from Worker Nodes (Current State).
  2. **Diff**: Calculates the delta between current state and manifest definitions (Desired State).
  3. **Act**: Triggers automated corrective actions (spawns missing Pods or terminates surplus Pods).

---

# Slide 5: Kubernetes Deployment & Zero-Downtime Rolling Updates
**Layout**: 2 Columns (Left: ReplicaSet Management | Right: Step-by-Step Rolling Update)
**Visual**: Phased transition gracefully terminating v1 Pods only after v2 Pods pass health checks.

- **Role of the Deployment Controller**:
  - Higher-level declarative abstraction managing lower-level **ReplicaSets**.
  - Enforces desired replica counts for high availability and automated self-healing.
- **The Rolling Update Strategy**:
  - Updating code from v1 to v2 creates a new ReplicaSet.
  - Kubernetes boots 1 new v2 Pod and waits for it to pass its Readiness check.
  - Only after v2 is actively serving traffic does K8s terminate 1 old v1 Pod.
  - Repeats until migration completes ➔ **Zero Downtime for end users**!

---

# Slide 6: Kubernetes Service: Stable Networking & Service Discovery
**Layout**: Service Load Balancer Diagram routing traffic to 3 Ephemeral Pods
**Visual**: Virtual ClusterIP with internal DNS distributing TCP requests to Pods matching target labels.

- **The Ephemeral IP Challenge**:
  - Pods are disposable. Whenever a Pod restarts or reschedules, it receives a brand-new internal IP.
  - Upstream consumers cannot hardcode downstream Pod IP addresses!
- **The Kubernetes Service Abstraction**:
  - Provides an immutable **Virtual IP (ClusterIP)** and a persistent internal DNS record:
    `http://reviews.default.svc.cluster.local:9080`
- **Dynamic Matching via Labels & Selectors**:
  - The Service uses label selectors (`selector: app: reviews`) to track healthy backing Pods.
  - `kube-proxy` transparently distributes incoming traffic across all matching endpoints.

---

# Slide 7: Self-Healing Architecture & The Three Health Probes
**Layout**: 3 Feature Cards
**Visual**: Stethoscope diagnostic flow: Startup Probe ➔ Liveness Probe ➔ Readiness Probe.

- **1. Startup Probe (Initialization Guard)**:
  - Protects slow-booting legacy apps (like Java Open Liberty) during heavy startup routines.
  - Suspends Liveness and Readiness checks until the app is fully initialized.
- **2. Liveness Probe (Deadlock Recovery)**:
  - Detects frozen processes or threadpool deadlocks.
  - If the probe fails, Kubernetes immediately **kills and restarts the container**.
- **3. Readiness Probe (Traffic Routing Gate)**:
  - Verifies whether the container is ready to accept incoming customer requests.
  - If failing, K8s temporarily ejects the Pod from the Service endpoint pool to prevent 502 errors.

---

# Slide 8: Production Manifest Analysis (`platform/kube/bookinfo.yaml`)
**Layout**: 2 Columns (Service Definition on Left | Deployment Specification on Right)
**Visual**: Direct mapping lines showing Service selectors binding to Deployment template labels.

```yaml
# 1. Stable Internal Layer 4 Service
apiVersion: v1
kind: Service
metadata:
  name: reviews
spec:
  ports:
  - port: 9080
    name: http
  selector:
    app: reviews # Matches Pod labels
---
# 2. Replicated Workload Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: reviews-v1
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: reviews
        version: v1
    spec:
      containers:
      - name: reviews
        image: docker.io/istio/examples-bookinfo-reviews-v1:1.20.0
```

---

# Slide 9: Live Verification: Pod Failure Simulation & Sub-3s Recovery
**Layout**: Terminal Execution Timeline + Recovery Milestones
**Visual**: Pod killed via `kubectl delete` replaced by a fresh running instance in 2.1 seconds.

- **Self-Healing Verification Walkthrough**:
  1. Inspect active running pods:
     `kubectl get pods -l app=productpage`
  2. Simulate catastrophic failure by forcibly deleting the active pod:
     `kubectl delete pod -l app=productpage`
  3. Observe the immediate cluster response:
     - `ReplicaSet Controller` detects available count drops from `1/1` to `0/1`.
     - Reconciliation loop triggers immediately: Scheduler assigns a node, Kubelet launches a replacement.
- **Empirical Results**: Replacement pod transitions to `2/2 Running` within **2.1 seconds**. End-user traffic experiences zero interruption!

---

# Slide 10: Kubernetes Architectural Evaluation & Trade-offs
**Layout**: 2-Column Balance Sheet (Platform Capabilities vs Operational Overhead)
**Visual**: Enterprise scale requiring advanced operational maturity.

| Core Kubernetes Advantages | Inherent Operational Challenges | Production Mitigation Strategy |
|---|---|---|
| **Autonomous Self-Healing**: Resilient 24/7 self-repair without manual sysadmin intervention. | **Steep Learning Curve**: Hundreds of complex abstractions (CRDs, CNI, CSI, RBAC). | Leverage Managed Kubernetes engines (GKE, EKS, AKS) to offload Control Plane toil. |
| **Declarative Infrastructure Standard**: Write YAML once, run identically across public and private clouds. | **Control Plane Overhead**: etcd and management components consume baseline CPU/RAM. | Conduct rigorous cluster capacity planning and define container Resource Quotas. |
| **Layer 4 Traffic Distribution**: Reliable round-robin TCP load balancing. | **Lacks Layer 7 Intelligence**: K8s Services cannot inspect HTTP headers or cookies. | Augment the cluster with an **Istio Service Mesh**! |
