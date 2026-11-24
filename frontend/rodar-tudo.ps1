<#
Sobe TODAS as versões do serviço (Java e Python, 4 protocolos cada) e o frontend.
Cada servidor abre na sua própria janela; para parar, é só fechar as janelas.

Uso (na raiz do repositório, com a branch frontend):
    powershell -ExecutionPolicy Bypass -File frontend\rodar-tudo.ps1

Opções:  -SemJava   sobe só as versões Python
         -SemPython sobe só as versões Java

Cada branch é colocada numa cópia separada (git worktree) na pasta "servidores",
ao lado do repositório, sempre na versão mais recente do GitHub (origin/<branch>).
Não altere arquivos nessas cópias: elas são atualizadas à força a cada execução.

Portas:
                REST    GraphQL   SOAP    gRPC
    Java        9081    9082      9083    9090
    Python      8001    8002      8003    50051
    Frontend    http://localhost:3000
#>
param([switch]$SemJava, [switch]$SemPython)
$ErrorActionPreference = "Stop"

$repo = (git -C $PSScriptRoot rev-parse --show-toplevel).Trim()
$base = Join-Path (Split-Path $repo -Parent) "servidores"
New-Item -ItemType Directory -Force $base | Out-Null

Write-Host "Buscando as branches no GitHub..." -ForegroundColor Cyan
git -C $repo fetch -q origin
git -C $repo worktree prune

function Preparar-Copia($nome, $branch) {
    $dir = Join-Path $base $nome
    if (Test-Path (Join-Path $dir ".git")) {
        git -C $dir checkout -q -f --detach "origin/$branch"
    } else {
        git -C $repo worktree add -q -f --detach $dir "origin/$branch"
    }
    return $dir
}

function Existe-Branch($branch) {
    git -C $repo rev-parse -q --verify "origin/$branch" *> $null
    return $LASTEXITCODE -eq 0
}

# Abre uma janela nova do PowerShell rodando $comando dentro de $pasta.
function Abrir-Janela($titulo, $pasta, $comando) {
    $script = "`$Host.UI.RawUI.WindowTitle = '$titulo'; Set-Location -LiteralPath '$pasta'; Write-Host '$titulo' -ForegroundColor Cyan; $comando"
    $codificado = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $codificado | Out-Null
}

function Preparar-Python($pasta) {
    $py = Join-Path $pasta ".venv\Scripts\python.exe"
    if (-not (Test-Path $py)) {
        Write-Host "  criando ambiente virtual em $pasta"
        python -m venv (Join-Path $pasta ".venv")
    }
    & $py -m pip install -q --disable-pip-version-check -r (Join-Path $pasta "requirements.txt")
    return $py
}

# ---------------- Python ----------------
if (-not $SemPython) {
    $python = @(
        @{ branch = "python-rest";    pasta = "python-rest";    cmd = "-m uvicorn main:app --port 8001" },
        @{ branch = "python-graphql"; pasta = "python-graphql"; cmd = "-m uvicorn main:app --port 8002" },
        @{ branch = "python-soap";    pasta = "python-soap";    cmd = "-m uvicorn main:app --port 8003" },
        @{ branch = "python-grpc";    pasta = "python-grpc";    cmd = "server.py 50051" }
    )
    foreach ($s in $python) {
        if (-not (Existe-Branch $s.branch)) { Write-Warning "Branch $($s.branch) não encontrada, pulando."; continue }
        Write-Host "Preparando $($s.branch)..." -ForegroundColor Cyan
        $dir = Join-Path (Preparar-Copia $s.branch $s.branch) $s.pasta
        $py = Preparar-Python $dir
        Abrir-Janela "Python - $($s.branch)" $dir "& '$py' $($s.cmd)"
    }
}

# ---------------- Java ----------------
if (-not $SemJava) {
    if (-not (Get-Command java -ErrorAction SilentlyContinue)) {
        Write-Warning "Java não encontrado no PATH; pulando as versões Java."
    } else {
        $java = @(
            @{ nome = "java-rest";    branch = "main";    args = "--server.port=9081" },
            @{ nome = "java-graphql"; branch = "graphql"; args = "--server.port=9082" },
            @{ nome = "java-soap";    branch = "soap";    args = "--server.port=9083" },
            @{ nome = "java-grpc";    branch = "grpc";    args = "--server.port=9084 --grpc.server.port=9090" }
        )
        foreach ($s in $java) {
            if (-not (Existe-Branch $s.branch)) { Write-Warning "Branch $($s.branch) não encontrada, pulando."; continue }
            Write-Host "Preparando $($s.nome) (branch $($s.branch))..." -ForegroundColor Cyan
            $dir = Join-Path (Preparar-Copia $s.nome $s.branch) "demo"
            # compila e roda na própria janela (a primeira compilação demora)
            $cmd = ".\mvnw.cmd -q -DskipTests package; if (`$LASTEXITCODE -eq 0) { " +
                   "`$jar = Get-ChildItem target\*.jar | Where-Object Name -notlike '*plain*' | Select-Object -First 1; " +
                   "java -jar `$jar.FullName $($s.args) }"
            Abrir-Janela "Java - $($s.nome)" $dir $cmd
        }
    }
}

# ---------------- Frontend ----------------
Write-Host "Preparando o frontend..." -ForegroundColor Cyan
$py = Preparar-Python $PSScriptRoot
Abrir-Janela "Frontend (http://localhost:3000)" $PSScriptRoot "& '$py' server.py"

Write-Host ""
Write-Host "Tudo iniciado. As versões Java levam cerca de 1 minuto para compilar e subir." -ForegroundColor Green
Write-Host "Abrindo http://localhost:3000 ..." -ForegroundColor Green
Start-Sleep -Seconds 4
Start-Process "http://localhost:3000"
