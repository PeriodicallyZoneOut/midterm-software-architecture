# Setup & Demo Automation Script for Topic 03 (Tường)
# Microservices, Kubernetes, Istio, Prometheus, Grafana
# Primary Project: Bookinfo (Canonical Istio Polyglot Microservices Sample)

[CmdletBinding()]
param (
    [switch]$CheckOnly,
    [switch]$InstallIstio,
    [switch]$DeployBookinfo,
    [switch]$DeployObservability,
    [switch]$ApplyCanaryReviews,
    [switch]$ResetRoutesV1,
    [switch]$PortForwardProductpage,
    [switch]$PortForwardGrafana
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     KIỂM TRA & TRIỂN KHAI TOPIC 03: BOOKINFO + ISTIO    " -ForegroundColor Cyan
Write-Host "   (Microservices Polyglot, K8s, Mesh, Prometheus/Grafana) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Kiểm tra kết nối Kubernetes Cluster
Write-Host "`n[1/6] Đang kiểm tra kết nối Kubernetes..." -ForegroundColor Yellow
try {
    $clusterInfo = kubectl cluster-info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [!] LỖI: Chưa kết nối được với cụm Kubernetes." -ForegroundColor Red
        Write-Host " Vui lòng bật Docker Desktop -> Settings -> Kubernetes -> Enable Kubernetes và đợi cluster sẵn sàng." -ForegroundColor Yellow
        exit 1
    }
    Write-Host " [+] Kubernetes cluster đang hoạt động bình thường!" -ForegroundColor Green
    kubectl get nodes
} catch {
    Write-Host " [!] Lỗi khi gọi kubectl: $_" -ForegroundColor Red
    exit 1
}

if ($CheckOnly) {
    Write-Host "`nTrạng thái Workloads hiện tại:" -ForegroundColor Cyan
    kubectl get pods -o wide
    kubectl get svc
    exit 0
}

# 2. Bật Istio sidecar injection cho namespace default
Write-Host "`n[2/6] Cấu hình Istio Sidecar Injection cho namespace default..." -ForegroundColor Yellow
kubectl label namespace default istio-injection=enabled --overwrite
Write-Host " [+] Đã gán nhãn istio-injection=enabled cho namespace default!" -ForegroundColor Green

# 3. Triển khai Bookinfo Application
Write-Host "`n[3/6] Triển khai Bookinfo Microservices (productpage, details, reviews v1/v2/v3, ratings)..." -ForegroundColor Yellow
$bookinfoManifest = Join-Path $PSScriptRoot "projects\bookinfo\source\platform\kube\bookinfo.yaml"
if (Test-Path $bookinfoManifest) {
    kubectl apply -f $bookinfoManifest
    Write-Host " [+] Đã apply manifests Bookinfo thành công!" -ForegroundColor Green
} else {
    Write-Host " [!] Không tìm thấy file $bookinfoManifest" -ForegroundColor Red
}

# 4. Triển khai Ingress Gateway & DestinationRules
Write-Host "`n[4/6] Cấu hình Istio Ingress Gateway & DestinationRules..." -ForegroundColor Yellow
$gatewayManifest = Join-Path $PSScriptRoot "projects\bookinfo\source\networking\bookinfo-gateway.yaml"
$drManifest = Join-Path $PSScriptRoot "projects\bookinfo\source\networking\destination-rule-all.yaml"

if (Test-Path $gatewayManifest) {
    kubectl apply -f $gatewayManifest
    Write-Host " [+] Đã áp dụng Istio Ingress Gateway (bookinfo-gateway)!" -ForegroundColor Green
}
if (Test-Path $drManifest) {
    kubectl apply -f $drManifest
    Write-Host " [+] Đã áp dụng DestinationRules (subsets v1, v2, v3)!" -ForegroundColor Green
}

# 5. Triển khai Addons Observability (Prometheus & Grafana)
Write-Host "`n[5/6] Triển khai Prometheus và Grafana Addons..." -ForegroundColor Yellow
$promManifest = Join-Path $PSScriptRoot "projects\istio\source\samples\addons\prometheus.yaml"
$grafanaManifest = Join-Path $PSScriptRoot "projects\istio\source\samples\addons\grafana.yaml"

if (Test-Path $promManifest) {
    kubectl apply -f $promManifest
    Write-Host " [+] Đã triển khai Prometheus addon!" -ForegroundColor Green
}
if (Test-Path $grafanaManifest) {
    kubectl apply -f $grafanaManifest
    Write-Host " [+] Đã triển khai Grafana addon!" -ForegroundColor Green
}

# 6. Kiểm tra trạng thái các Pods
Write-Host "`n[6/6] Trạng thái Workload hiện tại:" -ForegroundColor Yellow
kubectl get pods
Write-Host "`nTrạng thái Addons (istio-system):" -ForegroundColor Yellow
kubectl get pods -n istio-system

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " [+] HOÀN TẤT SETUP BOOKINFO!" -ForegroundColor Green
Write-Host " - Mở trang web:       kubectl port-forward svc/productpage 9080:9080" -ForegroundColor Cyan
Write-Host "   -> URL: http://localhost:9080/productpage" -ForegroundColor White
Write-Host " - Mở Grafana:         kubectl port-forward svc/grafana -n istio-system 3000:3000" -ForegroundColor Cyan
Write-Host "   -> URL: http://localhost:3000 (Istio Service Dashboard)" -ForegroundColor White
Write-Host " - Mở Prometheus:      kubectl port-forward svc/prometheus -n istio-system 9090:9090" -ForegroundColor Cyan
Write-Host "   -> URL: http://localhost:9090" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
