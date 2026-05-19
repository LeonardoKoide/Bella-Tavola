# 🔧 Guia de Setup do Bella Tavola

## Estrutura de Componentes

### 1. FastAPI Base (`src/`)
- **config.py**: Gerenciamento de configurações com Pydantic BaseSettings
- **main.py**: Aplicação FastAPI principal com exception handlers customizados
- **models/**: Modelos Pydantic para validação de entrada/saída
  - prato.py, bebida.py, pedido.py, reserva.py
- **routers/**: Implementação dos endpoints organizados por domínio
  - pratos.py, bebidas.py, pedidos.py, reservas.py

### 2. Machine Learning (`ml/`)
- **data_utils.py**: Geração de datasets sintéticos com reprodutibilidade
- **model_utils.py**: Funções para carregamento de modelos do HuggingFace Hub
- **train.py**: Pipeline de treinamento com scikit-learn RandomForest

### 3. Testes (`tests/`)
- **conftest.py**: Fixtures pytest e configuração do TestClient
- **test_saude.py**: Testes de health check (smoke tests)
- **test_contratos.py**: Testes de contrato da API

### 4. CI/CD (`.github/workflows/`)
- **ci.yml**: Pipeline com 2 jobs:
  1. Qualidade: formatação, imports, smoke tests
  2. Integração: testes completos com cache HuggingFace

## Instalação Passo a Passo

### Passo 1: Clonar e Navegar
```bash
cd C:\Users\Desktop\Bella-Tavola
```

### Passo 2: Criar Ambiente Virtual (Opcional mas Recomendado)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### Passo 3: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Configurar Variáveis de Ambiente
```bash
# Editar .env se necessário
# Adicionar HF_TOKEN se usar HuggingFace
```

### Passo 5: Rodar a API
```bash
# Desenvolvimento com hot-reload
uvicorn src.main:app --reload

# Produção
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

API disponível em: `http://localhost:8000`
Docs Swagger: `http://localhost:8000/docs`

## Teste da API

### Opção 1: cURL
```bash
# GET /pratos
curl http://localhost:8000/pratos

# POST /pratos
curl -X POST http://localhost:8000/pratos \
  -H "Content-Type: application/json" \
  -d '{"nome": "Lasagna", "categoria": "massa", "preco": 48.0}'
```

### Opção 2: Python
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://localhost:8000/pratos")
    print(response.json())
```

## Rodar Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas smoke tests
pytest tests/ -m smoke -v

# Com cobertura
pytest tests/ --cov=src --cov-report=html
```

## Docker

### Build
```bash
docker build -t bella-tavola:latest .
```

### Run
```bash
docker run -p 8000:8000 -e DEBUG=false bella-tavola:latest
```

### Docker Compose (Opcional)
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - HF_TOKEN=${HF_TOKEN}
    env_file:
      - .env
```

## Machine Learning Pipeline

### Treinar Modelo
```bash
cd ml
python train.py
```

Gera arquivo `model_fraude.pkl`

### Publicar no HuggingFace (Opcional)
```bash
# Requer HF_TOKEN configurado
python publicar.py
```

## Integração Contínua (GitHub Actions)

O arquivo `.github/workflows/ci.yml` define:

1. **Trigger**: Push em main/master ou Pull Request
2. **Job Qualidade** (ubuntu-latest):
   - Setup Python 3.11
   - Instalar deps
   - Black (format check)
   - Autoflake (unused imports)
   - Pytest smoke tests
3. **Job Integração** (apenas após push em main):
   - Cache HuggingFace
   - Pytest integration tests
   - HF_TOKEN via secrets

### Setup no GitHub
1. Ir em Settings > Secrets and variables > Actions
2. Adicionar `HF_TOKEN` se usar HuggingFace

## Troubleshooting

### ModuleNotFoundError: No module named 'src'
```bash
# Adicionar ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:C:\Users\Desktop\Bella-Tavola\src"
```

### Porta 8000 em uso
```bash
# Usar porta diferente
uvicorn src.main:app --port 8001
```

### Testes falhando
```bash
# Verificar imports
python -c "from src.main import app"

# Rodar com verbose
pytest tests/ -vv --tb=long
```

## Próximos Passos

1. ✅ Estrutura base criada
2. ✅ Testes configurados
3. ✅ CI/CD pipeline pronto
4. 📋 Adicionar autenticação (JWT)
5. 📋 Implementar banco de dados (SQLAlchemy)
6. 📋 Documentação OpenAPI personalizada
7. 📋 Logging centralizado
8. 📋 Métricas e monitoramento
