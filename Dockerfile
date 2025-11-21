FROM python:3.11-slim

# Metadados
LABEL maintainer="LEVESOL <contato@levesol.com.br>"
LABEL description="Sistema de Propostas Web - Energia Solar"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (cache layer)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório de logs
RUN mkdir -p logs

# Expor porta
EXPOSE 8182

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8182/health || exit 1

# Comando para rodar a aplicação
CMD ["python", "main.py"]
