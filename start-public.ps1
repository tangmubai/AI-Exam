$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $projectRoot

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    $python = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $python) {
    throw "未找到 Python。请先安装 Python 3。"
}

$cloudflared = Get-Command cloudflared -ErrorAction SilentlyContinue
if (-not $cloudflared) {
    throw "未找到 cloudflared。"
}

$serverProcess = $null
$tunnelProcess = $null
try {
    $serverProcess = Start-Process `
        -FilePath $python.Source `
        -ArgumentList @("$projectRoot\serve.py", "--host", "127.0.0.1", "--port", "8788") `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -PassThru

    $tunnelProcess = Start-Process `
        -FilePath $cloudflared.Source `
        -ArgumentList @("tunnel", "--config", "$projectRoot\cloudflared-aitest.yml", "run") `
        -WorkingDirectory $projectRoot `
        -WindowStyle Hidden `
        -PassThru

    Write-Host "Public site: https://aitest.sj-tu.com"
    Write-Host "Press Ctrl+C to stop the local server and tunnel."

    while (-not $serverProcess.HasExited -and -not $tunnelProcess.HasExited) {
        Start-Sleep -Seconds 2
        $serverProcess.Refresh()
        $tunnelProcess.Refresh()
    }

    if ($serverProcess.HasExited) {
        throw "Local server stopped with exit code $($serverProcess.ExitCode)."
    }
    throw "cloudflared stopped with exit code $($tunnelProcess.ExitCode)."
}
finally {
    if ($tunnelProcess -and -not $tunnelProcess.HasExited) {
        Stop-Process -Id $tunnelProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
}
