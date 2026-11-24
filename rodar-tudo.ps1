<#
Sobe TODAS as versões do serviço (Java e Python, 4 protocolos cada) e o frontend.
Cada servidor abre na sua própria janela; para parar, feche as janelas.

Uso: dois cliques em rodar-tudo.bat, ou
     powershell -ExecutionPolicy Bypass -File rodar-tudo.ps1

Opções:  -SemJava     sobe só as versões Python
         -SemPython   sobe só as versões Java
         -Recompilar  força a recompilação das versões Java

Portas:
                REST    GraphQL   SOAP    gRPC
    Java        9081    9082      9083    9090
    Python      8001    8002      8003    50051
    Frontend    http://localhost:3000
#>
param([switch]$SemJava, [switch]$SemPython, [switch]$Recompilar)
$ErrorActionPreference = "Stop"
$raiz = $PSScriptRoot

function Titulo($texto) { Write-Host ""; Write-Host "== $texto" -ForegroundColor Cyan }

# Abre uma janela nova do PowerShell rodando $comando dentro de $pasta.
function Abrir-Janela($titulo, $pasta, $comando) {
    $script = "`$Host.UI.RawUI.WindowTitle = '$titulo'; Set-Location -LiteralPath '$pasta'; " +
              "Write-Host '$titulo' -ForegroundColor Cyan; $comando"
    $codificado = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $codificado | Out-Null
}

function Porta-Ocupada($porta) {
    return [bool](Get-NetTCPConnection -State Listen -LocalPort $porta -ErrorAction SilentlyContinue)
}

# ---------------- verificações ----------------
$portas = @(3000)
if (-not $SemPython) { $portas += 8001, 8002, 8003, 50051 }
if (-not $SemJava)   { $portas += 9081, 9082, 9083, 9084, 9090 }
$ocupadas = $portas | Where-Object { Porta-Ocupada $_ }
if ($ocupadas) {
    Write-Host "As portas $($ocupadas -join ', ') já estão em uso." -ForegroundColor Red
    Write-Host "Feche as janelas de uma execução anterior e rode de novo." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python não encontrado. Instale o Python 3.10+ (marque 'Add to PATH')." -ForegroundColor Red
    exit 1
}
if (-not $SemJava -and -not (Get-Command java -ErrorAction SilentlyContinue)) {
    Write-Host "Java não encontrado: subindo só as versões Python. Instale o JDK 17+ para as versões Java." -ForegroundColor Yellow
    $SemJava = $true
}

# ---------------- ambiente Python (um só para tudo) ----------------
Titulo "Preparando o ambiente Python"
$py = Join-Path $raiz ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Criando ambiente virtual (.venv)..."
    python -m venv (Join-Path $raiz ".venv")
}
& $py -m pip install -q --disable-pip-version-check -r (Join-Path $raiz "requirements.txt")
if ($LASTEXITCODE -ne 0) { Write-Host "Falha ao instalar as dependências Python." -ForegroundColor Red; exit 1 }

# ---------------- Java: compila (só na primeira vez) ----------------
$java = @(
    @{ nome = "rest";    args = "--server.port=9081" },
    @{ nome = "graphql"; args = "--server.port=9082" },
    @{ nome = "soap";    args = "--server.port=9083" },
    @{ nome = "grpc";    args = "--server.port=9084 --grpc.server.port=9090" }
)
if (-not $SemJava) {
    foreach ($s in $java) {
        $pasta = Join-Path $raiz "java\$($s.nome)"
        $jar = Get-ChildItem (Join-Path $pasta "target\*.jar") -ErrorAction SilentlyContinue |
               Where-Object Name -notlike "*plain*" | Select-Object -First 1
        if ($Recompilar -or -not $jar) {
            Titulo "Compilando Java $($s.nome) (na primeira vez baixa as dependências e demora alguns minutos)"
            Push-Location $pasta
            & .\mvnw.cmd -q -DskipTests package
            $ok = $LASTEXITCODE -eq 0
            Pop-Location
            if (-not $ok) { Write-Host "Falha ao compilar java\$($s.nome)." -ForegroundColor Red; exit 1 }
            $jar = Get-ChildItem (Join-Path $pasta "target\*.jar") | Where-Object Name -notlike "*plain*" | Select-Object -First 1
        }
        $s.jar = $jar.FullName
    }
}

# ---------------- sobe tudo ----------------
Titulo "Subindo os servidores"
if (-not $SemPython) {
    Abrir-Janela "Python REST :8001"    (Join-Path $raiz "python\rest")    "& '$py' -m uvicorn main:app --port 8001"
    Abrir-Janela "Python GraphQL :8002" (Join-Path $raiz "python\graphql") "& '$py' -m uvicorn main:app --port 8002"
    Abrir-Janela "Python SOAP :8003"    (Join-Path $raiz "python\soap")    "& '$py' -m uvicorn main:app --port 8003"
    Abrir-Janela "Python gRPC :50051"   (Join-Path $raiz "python\grpc")    "& '$py' server.py 50051"
}
if (-not $SemJava) {
    foreach ($s in $java) {
        Abrir-Janela "Java $($s.nome)" (Join-Path $raiz "java\$($s.nome)") "java -jar '$($s.jar)' $($s.args)"
    }
}
Abrir-Janela "Frontend :3000" (Join-Path $raiz "frontend") "& '$py' server.py"

Write-Host ""
Write-Host "Tudo iniciado! As versões Java levam uns 20 segundos para ficar prontas." -ForegroundColor Green
Write-Host "Abrindo http://localhost:3000 ..." -ForegroundColor Green
Start-Sleep -Seconds 5
Start-Process "http://localhost:3000"
