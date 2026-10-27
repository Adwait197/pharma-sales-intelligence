# Load variables from .env into this PowerShell session (for dbt)
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)=(.*)$') {
        Set-Item -Path "env:$($matches[1].Trim())" -Value $matches[2].Trim()
    }
}
Write-Host "Loaded .env into this session"