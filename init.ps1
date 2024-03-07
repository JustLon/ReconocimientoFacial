# Mensaje de bienvenida
Write-Host "Bienvenido al script de PowerShell del Reconicmiento Facial de los Agentes P!"
Write-Host "Iniciando"
Start-Sleep -Milliseconds 30
Write-Host "Iniciando."
Start-Sleep -Milliseconds 40
Write-Host "Iniciando.."
Start-Sleep -Milliseconds 25

# Ruta del entorno virtual
$venvPath = ".\venv\Scripts\activate"

# Verificar si existe el entorno virtual
if (Test-Path $venvPath) {
    # Activar el entorno virtual
    Write-Host "Activando el entorno virtual..."
    & $venvPath
    Start-Sleep -Seconds 1  # Delay de 1 segundo
    Write-Host "Entorno virtual activado."
} else {
    Write-Host "No se encontró el entorno virtual en la ruta especificada."
    exit
}

# Ejecutar el archivo main.py
Write-Host "Ejecutando main.py..."
py main.py
Start-Sleep -Seconds 1  # Delay de 1 segundo
Write-Host "main.py ejecutado."
