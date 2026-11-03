# AI Slide Generation Guide & Master Prompts

This directory (`slides/generate/`) contains presentation source files specifically formatted and optimized for copy-pasting directly into modern AI slide generation platforms such as **Gamma.app**, **Tome.app**, **SlidesGPT**, **Canva AI**, **Claude**, and **ChatGPT**.

---

## 🏆 ULTIMATE 10-MINUTE ALL-IN-ONE PRESENTATION (1 SLIDE PER TOPIC)

> ⭐️ **USE THIS FILE FOR YOUR 10-MINUTE DEFENSE**:  
> 👉 [`final-presentation-ai.md`](./final-presentation-ai.md)  
> 
> - **Structure**: Exactly **10 slides for a 10-minute presentation** (60 seconds per slide).
> - **Design**: **1 slide per core topic**, prominently showcasing the **Software Architecture**, ASCII topological diagrams, code mapping, visual prompts, and exact 60-second presenter speaking notes!
> - **Slide Breakdown**:
>   1. **System Overview**: 4-Tier Cloud-Native Architecture Blueprint
>   2. **Microservices**: Domain Decomposition (DDD) & Polyglot Architecture
>   3. **Bookinfo**: 4-Service Polyglot Implementation & Async Fan-Out
>   4. **Docker**: Containerization & Multi-Stage Build Architecture (`reviews/Dockerfile`)
>   5. **Kubernetes**: Cluster Orchestration & 2/2 Ready Pod Architecture
>   6. **Istio**: Service Mesh Control Plane vs Data Plane Architecture (iptables intercept)
>   7. **Prometheus**: Time-Series Storage (TSDB) & Pull Scrape Architecture (`:15090`)
>   8. **Grafana**: SRE Telemetry Correlation & Cross-Layer Visualization Architecture
>   9. **Live Verification**: 4-Step End-to-End Architectural Demonstration & Chaos Test
>   10. **Architectural Retrospective**: Monolith vs Cloud-Native Mesh Trade-offs

---

## 🌟 3 Master Consolidated Decks (Alternative Option)

Each master deck combines tightly related technologies into a cohesive **10-slide, 10-minute presentation** covering architectural theory, source code implementation, and production verification:

| Master Deck | Combined Technologies | Core Architectural Themes |
|:---:|---|---|
| 👑 [`01-microservices-bookinfo-istio.md`](./01-microservices-bookinfo-istio.md) | **Microservices + Bookinfo + Istio Service Mesh** | Bounded contexts, Polyglot topology (Python, Ruby, Java, Node.js), `productpage.py` aggregator, `reviews` v1/v2/v3, header propagation, Envoy intercept (15001/15006), Ingress Gateway, Canary user `jason`, fault injection, mTLS. |
| 👑 [`02-docker-kubernetes.md`](./02-docker-kubernetes.md) | **Docker + Kubernetes** | VMs vs Containers, Linux Namespaces/cgroups/Overlay2, multi-stage builds (`reviews/Dockerfile` 850MB ➔ 210MB), layer cache, Control Plane vs Worker Nodes, 2/2 ready Pods, Deployments, ClusterIP Services, self-healing demo (2.1s). |
| 👑 [`03-prometheus-grafana.md`](./03-prometheus-grafana.md) | **Prometheus + Grafana** | Observability pillars, Prometheus pull model `:15090`, time-series data model, PromQL golden signals (RPS, Latency P95, 5xx ratios), Grafana SRE dashboards, cross-layer CPU/RAM correlation, dynamic variables, alerting. |

---

## 📁 7 Individual Single-Topic Decks (If Single-Topic Slides Are Needed)

| File | Topic | Focus for AI Slide Generation |
|---|---|---|
| [`01-microservices-ai.md`](./01-microservices-ai.md) | **Microservices Architecture** | Monolith decomposition, Bounded Contexts, Polyglot design, Aggregator pattern, Trade-offs |
| [`02-docker-ai.md`](./02-docker-ai.md) | **Docker & Containerization** | VMs vs Containers, Linux Namespaces/cgroups, Multi-stage builds, Layer caching, Security |
| [`03-kubernetes-ai.md`](./03-kubernetes-ai.md) | **Kubernetes Orchestration** | Control Plane vs Workers, 2/2 Pods, Rolling updates, Service Discovery, Self-healing |
| [`04-istio-ai.md`](./04-istio-ai.md) | **Istio Service Mesh** | Envoy intercept (15001/15006), Ingress Gateway, Canary routing, Fault injection, mTLS |
| [`05-prometheus-ai.md`](./05-prometheus-ai.md) | **Prometheus Monitoring** | Pull model `:15090`, Multi-dimensional labels, 4 metric types, PromQL (RPS, P95, SLOs) |
| [`06-grafana-ai.md`](./06-grafana-ai.md) | **Grafana Observability** | DataSource provisioning, Mesh & Service Dashboards, Resource correlation, Dynamic variables |
| [`07-bookinfo-ai.md`](./07-bookinfo-ai.md) | **Bookinfo Architecture** | 4-microservice topology, Tracing header propagation, Reviews v1/v2/v3, 4-step live demo |

---

## 🚀 30-Second Generation Workflow Using Gamma.app (Recommended)

**Gamma.app** is currently the industry-leading AI presentation engine for technical and software engineering decks:

1. Visit **[gamma.app](https://gamma.app)** and log in.
2. Click **Create New** ➔ Select **Paste in text** (or Import markdown file).
3. Select Format: **Presentation** ➔ Number of cards: **10 slides**.
4. Open the topic file you need (e.g., `01-microservices-bookinfo-istio.md`), copy the entire text, and paste it into Gamma's input box.
5. Select a Dark / Modern Engineering Theme: **"Obsidian"**, **"Neon Cyan"**, or **"Midnight"**.
6. Click **Generate Presentation**.
7. In ~30 seconds, Gamma will automatically generate a stunning 10-slide deck with structured feature cards, syntax-highlighted code blocks, comparison matrices, and contextual diagrams.
8. Click **Export** ➔ Download as **PowerPoint (.pptx)** or **PDF** for your defense presentation!

---

## 🎯 Master Prompt for Custom AI Refinement

If you use ChatGPT Plus, Claude 3.5 Sonnet, or Gamma's AI customizer, supply this prompt:

```text
Act as a Principal Cloud-Native Software Architect and Senior SRE Lead.
Create a high-impact, 10-slide technical presentation based on the provided markdown text.
Tone: Professional, architectural, engineering-focused, crisp.
Design Theme: Modern Dark Mode (#0d1117 background, cyan/blue accent #58a6ff, high-contrast code snippets).
Layout Guidelines: Strictly avoid plain walls of text. Utilize 2-column comparative splits, 3-column feature cards, bold conceptual keywords, and cleanly formatted syntax-highlighted code blocks.
Include explicit architectural diagram prompts for each slide to illustrate microservices communication and Kubernetes topologies.
```
