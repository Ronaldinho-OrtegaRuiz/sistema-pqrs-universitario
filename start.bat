@echo off
echo ========================================
echo   Iniciando Bot Libertador
echo ========================================
echo.

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias si es necesario
echo.
echo Verificando dependencias...
pip install -r requirements.txt --quiet

echo.
echo ========================================
echo   Servidor iniciando en http://localhost:8000
echo   Presiona Ctrl+C para detener
echo ========================================
echo.

REM Iniciar el servidor
python main.py

