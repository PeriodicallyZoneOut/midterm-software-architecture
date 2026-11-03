# Master Deck 2: Containerization with Docker & Orchestration with Kubernetes
**Presenter**: Tuong (10-Minute Technical Architecture Defense)
**Target Slides**: 10 Slides
**Design Theme**: Modern Dark Mode, Docker Cyan (#0db7ed) & Kubernetes Blue (#326ce5), Infrastructure Grid

---

# Slide 1: The Containerization Paradigm: Overcoming "Works on My Machine"
**Layout**: 2 Columns (Left: Environment Drift Chaos | Right: The Docker Container Solution)
**Visual**: Developer workstation running Java 17 vs production server failing on Java 11.

- **The Legacy Deployment Nightmare**:
  - Code compiles cleanly locally but fails catastrophically on production due to library and runtime drift.
  - "Dependency Hell" when hosting multiple distinct services on a single shared operating system.
  - Manual server provisioning leads to snowflake configurations that are impossible to replicate.
- **Docker's Paradigm Shift**:
  - Packages application code, runtime, system binaries, and configuration into an immutable **Docker Image**.
  - **"Build Once, Run Anywhere"**: Absolute parity from local developer laptop to hybrid production clouds.

---

# Slide 2: Architectural Face-Off: Containers vs Virtual Machines (VMs)
**Layout**: 2-Column Comparison Table + Hypervisor vs Container Engine Diagram
**Visual**: Heavyweight VM stack with redundant Guest OS layers contrasted with lightweight containers sharing the Host OS kernel.

| Architectural Dimension | Virtual Machine (VM) | Container (Docker) |
|---|---|---|
| **Architecture Stack** | Requires a complete, independent **Guest OS** | **Shares the Host OS Linux Kernel** directly |
| **Disk Footprint** | Gigabytes to tens of Gigabytes (GBs) | Tens to hundreds of Megabytes (MBs) |
| **Boot Startup Time** | Minutes (Full OS kernel initialization) | **Milliseconds** (Just starting a native process) |
| **Memory Allocation** | Static RAM reserved for Guest OS overhead | Dynamic allocation: consumes only active memory |
| **Isolation Boundary** | Hardware-level virtualization via Hypervisor | OS-level process isolation via Linux kernel primitives |

---

# Slide 3: Under the Hood: Linux Kernel Primitives Powering Containers
**Layout**: 3 Feature Cards
**Visual**: Three foundational pillars: Namespaces (Scope), cgroups (Quota), OverlayFS (Storage).

- **1. Linux Namespaces (Process Isolation & Boundary)**:
  - `PID Namespace`: The containerized app sees itself as PID 1, completely blind to host processes.
  - `NET Namespace`: Provides isolated virtual network interfaces, routing tables, and IP addresses.
  - `MNT Namespace`: Isolates file system mount points to the container's rootfs.
- **2. Control Groups - cgroups (Resource Metering & Quotas)**:
  - Enforces strict upper ceilings: e.g., restrict container to maximum 1 CPU Core and 512MB RAM.
  - Prevents rogue memory leaks from starving the underlying host.
- **3. Union File System - Overlay2 (Layered Storage & Copy-on-Write)**:
  - Stacks immutable read-only image layers into a single unified view with a thin writable layer on top.

---

# Slide 4: Multi-Stage Builds: Solving Image Bloat (`src/reviews/Dockerfile`)
**Layout**: 2 Columns (Stage 1: Gradle Builder | Stage 2: Open Liberty Runtime)
**Visual**: Artifact transfer arrow copying reviews.war from the builder stage into the final slim runtime.

- **The Single-Stage Anti-Pattern**: Shipping compilers, build caches, and JDKs (~850MB) to production wastes bandwidth and expands the CVE attack surface.
- **The Multi-Stage Solution**:
```dockerfile
# STAGE 1: Compilation & Packaging (Builder)
FROM gradle:7.3.3-jdk11 AS builder
WORKDIR /home/gradle/src
COPY --chown=gradle:gradle . .
RUN gradle build --no-daemon

# STAGE 2: Production Execution (Runtime)
FROM open-liberty:21.0.0.12-kernel-slim-openj9-ubi
# Copy ONLY the compiled binary into the lean base runtime
COPY --from=builder /home/gradle/src/build/libs/reviews.war /config/apps/
COPY --from=builder /home/gradle/src/server.xml /config/
EXPOSE 9080
USER 1001
CMD ["server", "run"]
```
- Slashes final image footprint from **850MB down to 210MB** (75% bandwidth reduction).

---

# Slide 5: Layer Caching Strategies & Container Security
**Layout**: 2 Columns (Optimized Dockerfile on Left | Security Best Practices on Right)
**Visual**: Docker build cache pipeline: Cache Hit vs Invalidation + Security Shield Icon.

- **Maximizing Layer Cache Hits (`productpage/Dockerfile`)**:
```dockerfile
# Step 1: Copy ONLY dependency manifests first
COPY requirements.txt /opt/microservices/
# Step 2: Install dependencies (CACHED if requirements.txt is unchanged)
RUN pip install --no-cache-dir -r requirements.txt
# Step 3: Copy application source code LAST (Changes often without triggering pip install)
COPY . /opt/microservices/
```
  - Reduces CI/CD rebuild cycles from **3 minutes down to 5 seconds**!
- **Container Hardening Standards**:
  - **Non-Root Execution**: Enforce `USER 1001` to eliminate container breakout risks.
  - **Minimal Base Images**: Standardize on Distroless, Alpine, or UBI Minimal.
  - **Automated CVE Scanning**: Integrate Trivy / Docker Scout into CI pipelines.

---

# Slide 6: Production Orchestration: Why Kubernetes is Essential
**Layout**: 2 Columns (Left: Chaos of Raw Docker at Scale | Right: The Kubernetes Automation Engine)
**Visual**: Overwhelmed sysadmin managing dozens of fragmented VMs vs Kubernetes reconciling cluster state automatically.

- **The Multi-Container Operational Challenge**:
  - How do you schedule 50+ containers across multiple VMs with dynamic resource quotas?
  - When an underlying physical server dies, who resurrects the workloads elsewhere?
  - Container IPs change continuously upon restart; how do services reliably discover each other?
- **The Kubernetes (K8s) Solution**:
  - The de facto open-source container orchestration engine originally developed by Google.
  - Automates scheduling, load balancing, health monitoring, and horizontal autoscaling.

---

# Slide 7: Kubernetes Architecture: Control Plane vs Worker Nodes
**Layout**: 2-Tier Stack Diagram (Brain Tier on top, Execution Tier below)
**Visual**: Control Plane components (API Server, etcd, Scheduler, Controller) dispatching state via Kubelet to Worker Nodes.

- **1. The Control Plane (The Cluster's Brain)**:
  - `kube-apiserver`: The central administrative REST gateway validating and configuring cluster data.
  - `etcd`: Highly available distributed key-value store holding complete desired state.
  - `kube-scheduler`: Evaluates CPU/RAM constraints and node affinities to place incoming Pods.
  - `kube-controller-manager`: Runs continuous reconciliation loops to enforce desired state.
- **2. Worker Nodes (The Workload Execution Engine)**:
  - `kubelet`: Primary node agent ensuring declared containers are running and healthy.
  - `kube-proxy`: Maintains network rules and implements Layer 4 TCP load balancing.
  - `Container Runtime`: Low-level engine executing containers (containerd, CRI-O).

---

# Slide 8: The Pod Abstraction & Sidecar Pattern (The 2/2 Ready Pod)
**Layout**: 2 Columns (Left: Pod Fundamentals | Right: 2/2 Ready Bookinfo Pod Structure)
**Visual**: A Pod perimeter enclosing two containers sharing a single IP, network namespace, and localhost.

- **The Atomic Pod Unit**:
  - The smallest schedulable execution unit in Kubernetes.
  - Encloses one or more tightly coupled containers sharing network namespaces and storage volumes.
  - Inter-container communication happens over near-zero latency `localhost`.
- **The Bookinfo "2/2 Ready" Pod Architecture**:
  - **Container 1**: Core business application (Python `productpage`, Ruby `details`, Java `reviews`).
  - **Container 2**: Infrastructure auxiliary proxy (`istio-proxy` / Envoy).
  - Inspecting running workloads demonstrates 100% sidecar adoption:
```text
NAME                              READY   STATUS    RESTARTS   AGE
productpage-v1-d5789fdfb-k8x5n    2/2     Running   0          5h
reviews-v1-7598cc9867-q2j5d       2/2     Running   0          5h
```

---

# Slide 9: Declarative Management, Rolling Updates & Self-Healing
**Layout**: 3 Feature Cards
**Visual**: Reconciliation loop diagram + Phased rolling update progression + Sub-3s recovery timeline.

- **1. Declarative Reconciliation Loop**:
  - Continuously observes current cluster state, computes delta against manifests, and automatically acts to converge state.
- **2. Zero-Downtime Rolling Updates**:
  - Kubernetes spawns 1 new v2 Pod, validates its Readiness check, and only then drains and terminates 1 old v1 Pod.
- **3. Autonomous Self-Healing Verified**:
  - When a running Pod is forcibly deleted (`kubectl delete pod -l app=productpage`):
  - ReplicaSet Controller immediately detects `0/1` availability and commands Scheduler to spawn a replacement.
  - **Empirical Result**: Replacement Pod reaches `2/2 Running` in **2.1 seconds** with zero customer downtime!

---

# Slide 10: Container Platform Architectural Trade-offs & Lessons
**Layout**: 2-Column Balance Sheet (Platform Capabilities vs Operational Costs)
**Visual**: Balance scales weighing Operational Resilience against Platform Complexity.

| Platform Superpowers Gained | Concrete Operational Costs | Production Engineering Solutions |
|---|---|---|
| **Absolute Execution Parity**: Eliminates environment drift from dev to production. | **Ephemeral Storage Management**: Local filesystem data vanishes when containers die. | Mount external Persistent Volumes (PV/PVC). |
| **Autonomous Self-Healing**: Resilient 24/7 self-repair without manual sysadmin intervention. | **Steep Learning Curve**: High cognitive overhead managing hundreds of K8s resources. | Adopt Managed K8s engines (GKE, EKS, AKS) to offload Control Plane management. |
| **Standardized Infrastructure-as-Code**: Declarative YAML manifests version-controlled in Git. | **Layer 4 Networking Limitations**: K8s Services cannot inspect HTTP headers or cookies. | Augment the cluster with an **Istio Service Mesh**! |

