# Setup & Demo Automation Script for Topic 01 (Nhat Anh)
# Quality Attributes: Scalability & Security
# Primary Projects: Online Boutique (Scalability & Locust) & ScriptHammer (Security & RLS)

[CmdletBinding()]
param (
    [switch]$CheckOnly,
    [switch]$DeployBoutique,
    [switch]$CheckLocust,
    [switch]$SetLoadHigh,
    [switch]$SetLoadBaseline,
    [switch]$ScaleFrontend,
    [switch]$ResetScale,
    [switch]$AuditSecurity
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  KIEM TRA & TRIEN KHAI TOPIC 01: QUALITY ATTRIBUTES     " -ForegroundColor Cyan
Write-Host " (Scalability: Online Boutique | Security: ScriptHammer) " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Kiem tra ket noi Kubernetes Cluster
Write-Host "`n[1/5] Kiem tra ket noi cum Kubernetes..." -ForegroundColor Yellow
try {
    $clusterInfo = kubectl cluster-info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host " [!] LOI: Chua ket noi duoc voi cum Kubernetes." -ForegroundColor Red
        Write-Host " Vui long mo Docker Desktop -> Settings -> Kubernetes -> Enable Kubernetes va doi san sang." -ForegroundColor Yellow
        exit 1
    }
    Write-Host " [+] Kubernetes cluster dang hoat dong binh thuong!" -ForegroundColor Green
    kubectl get nodes
} catch {
    Write-Host " [!] Loi khi goi kubectl: $_" -ForegroundColor Red
    exit 1
}

# 2. Xu ly cac co dac thu (Flags)
if ($AuditSecurity) {
    Write-Host "`n[SECURITY AUDIT] Kiem tra cac co che bao mat tren ScriptHammer..." -ForegroundColor Cyan
    $scripthammerRoot = Join-Path $PSScriptRoot "projects\scripthammer\source"
    
    # Check Gitleaks
    $gitleaksFile = Join-Path $scripthammerRoot ".gitleaks.toml"
    if (Test-Path $gitleaksFile) {
        Write-Host " [+] Da tim thay cau hinh chong lo secret (SAST): .gitleaks.toml" -ForegroundColor Green
    }
    
    # Check Supabase RLS migrations
    $migrationFile = Join-Path $scripthammerRoot "supabase\migrations\20251006_complete_monolithic_setup.sql"
    if (Test-Path $migrationFile) {
        $rlsCount = (Select-String -Path $migrationFile -Pattern "ENABLE ROW LEVEL SECURITY").Count
        Write-Host " [+] Da tim thay $rlsCount bang duoc kich hoat Supabase Row Level Security (RLS)!" -ForegroundColor Green
    }
    
    # Check Auth Rate Limiter
    $rateLimitFile = Join-Path $scripthammerRoot "src\lib\auth\auth-rate-limit.ts"
    if (Test-Path $rateLimitFile) {
        Write-Host " [+] Da tim thay bo loc chong Brute-force & Account Enumeration: auth-rate-limit.ts" -ForegroundColor Green
    }
    exit 0
}

if ($CheckLocust) {
    Write-Host "`n[LOCUST METRICS] Dang lay bang thong ke tai tu loadgenerator..." -ForegroundColor Cyan
    kubectl logs deployment/loadgenerator -c main --tail=25
    exit 0
}

if ($SetLoadHigh) {
    Write-Host "`n[LOAD TEST] Nang tai len muc cao (50 users, 5 spawn rate)..." -ForegroundColor Yellow
    kubectl set env deployment/loadgenerator USERS="50" RATE="5"
    Write-Host " [+] Da cap nhat bien moi truong tai. Pod loadgenerator dang ap dung muc tai moi!" -ForegroundColor Green
    exit 0
}

if ($SetLoadBaseline) {
    Write-Host "`n[LOAD TEST] Ha tai ve muc chuan Baseline (10 users, 1 spawn rate)..." -ForegroundColor Yellow
    kubectl set env deployment/loadgenerator USERS="10" RATE="1"
    Write-Host " [+] Da reset ve muc tai chuan (10 users)!" -ForegroundColor Green
    exit 0
}

if ($ScaleFrontend) {
    Write-Host "`n[SCALABILITY] Mo rong Horizontal Scaling cho frontend (1 -> 3 Replicas)..." -ForegroundColor Yellow
    kubectl scale deployment/frontend --replicas=3
    Write-Host " [+] Da gui lenh scale. Kiem tra trang thai Pods:" -ForegroundColor Green
    kubectl get pods -l app=frontend
    exit 0
}

if ($ResetScale) {
    Write-Host "`n[SCALABILITY] Dua frontend ve cau hinh 1 Replica ban dau..." -ForegroundColor Yellow
    kubectl scale deployment/frontend --replicas=1
    Write-Host " [+] Da dua frontend ve 1 Pod!" -ForegroundColor Green
    exit 0
}

if ($CheckOnly) {
    Write-Host "`n[2/5] Trang thai Pods Online Boutique (Scalability under test):" -ForegroundColor Cyan
    kubectl get pods -l "app in (frontend,cartservice,checkoutservice,productcatalogservice,recommendationservice,loadgenerator)"
    
    Write-Host "`n[3/5] Trang thai Dich vu & Cong truy cap:" -ForegroundColor Cyan
    kubectl get svc frontend-external frontend
    
    Write-Host "`n[4/5] Kiem tra phan hoi HTTP toi frontend:" -ForegroundColor Cyan
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing -TimeoutSec 3
        Write-Host " [+] Truy cap http://localhost thanh cong (HTTP StatusCode: $($resp.StatusCode))!" -ForegroundColor Green
    } catch {
        Write-Host " [!] Cong 80 chua mo truc tiep. Ban co the chay port-forward:" -ForegroundColor Yellow
        Write-Host "     kubectl port-forward svc/frontend 8080:80" -ForegroundColor White
    }
    
    Write-Host "`n[5/5] Tom tat thong ke tai tu Locust (real-time RPS & Latency):" -ForegroundColor Cyan
    kubectl logs deployment/loadgenerator -c main --tail=16
    exit 0
}

# 3. Trien khai Online Boutique neu can
Write-Host "`n[2/5] Kiem tra va Trien khai Online Boutique Microservices..." -ForegroundColor Yellow
$manifestPath = Join-Path $PSScriptRoot "projects\online-boutique\source\release\kubernetes-manifests.yaml"
if (Test-Path $manifestPath) {
    kubectl apply -f $manifestPath
    Write-Host " [+] Da apply manifests Online Boutique thanh cong!" -ForegroundColor Green
} else {
    Write-Host " [!] Khong tim thay file $manifestPath" -ForegroundColor Red
}

# 4. Cap nhat giao dien hien dai (Modernized Storefront UI)
$styleFile = Join-Path $PSScriptRoot "projects\online-boutique\source\src\frontend\static\styles\styles.css"
$patchFile = Join-Path $PSScriptRoot "frontend-style-patch.yaml"
if ((Test-Path $styleFile) -and (Test-Path $patchFile)) {
    Write-Host "`n[+] Dang ap dung giao dien moi (Modern SaaS / Storefront UI)..." -ForegroundColor Yellow
    kubectl create configmap frontend-custom-style --from-file=styles.css=$styleFile --dry-run=client -o yaml | kubectl apply -f - | Out-Null
    kubectl patch deployment frontend --patch-file $patchFile | Out-Null
    Write-Host " [+] Giao dien moi da duoc cap nhat truc tiep vao Frontend Pods!" -ForegroundColor Green
}

Write-Host "`n[3/5] Kiem tra trang thai trien khai Pods..." -ForegroundColor Yellow
kubectl get pods -l "app in (frontend,cartservice,checkoutservice,productcatalogservice,recommendationservice,loadgenerator)"

Write-Host "`n[4/5] Kiem tra cong ket noi..." -ForegroundColor Yellow
kubectl get svc frontend-external

Write-Host "`n[5/5] Hoan tat trien khai Topic 01!" -ForegroundColor Green
Write-Host "----------------------------------------------------------" -ForegroundColor DarkGray
Write-Host " HUONG DAN TRUY CAP & DEMO:" -ForegroundColor Cyan
Write-Host " 1. Web Online Boutique: http://localhost (hoac port-forward port 8080)" -ForegroundColor White
Write-Host " 2. Xem so lieu Locust:   .\setup-and-run.ps1 -CheckLocust" -ForegroundColor White
Write-Host " 3. Tang tai thi nghiem: .\setup-and-run.ps1 -SetLoadHigh" -ForegroundColor White
Write-Host " 4. Scale Pod Frontend:  .\setup-and-run.ps1 -ScaleFrontend" -ForegroundColor White
Write-Host " 5. Soi ma bao mat:      .\setup-and-run.ps1 -AuditSecurity" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
