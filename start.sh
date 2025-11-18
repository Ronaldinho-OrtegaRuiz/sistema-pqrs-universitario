#!/bin/bash

echo "========================================"
echo "  Iniciando Bot Libertador"
echo "========================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias si es necesario
echo ""
echo "Verificando dependencias..."
pip install -r requirements.txt --quiet

echo ""
echo "========================================"
echo "  Servidor iniciando en http://localhost:8000"
echo "  Presiona Ctrl+C para detener"
echo "========================================"
echo ""

# Iniciar el servidor
python main.py

