# 🍝 Bella Tavola API

Uma API robusta para gerenciamento de restaurante italiano, construída com **FastAPI**, **MLOps** e **CI/CD** com GitHub Actions.

## 📋 Estrutura do Projeto

```
bella-tavola/
├── src/                      # Código principal da aplicação
│   ├── config.py            # Configurações com BaseSettings
│   ├── main.py              # Aplicação FastAPI
│   ├── models/              # Modelos Pydantic
│   │   ├── prato.py
│   │   ├── bebida.py
│   │   ├── pedido.py
│   │   └── reserva.py
│   └── routers/             # Endpoints da API
│       ├── pratos.py
│       ├── bebidas.py
│       ├── pedidos.py
│       └── reservas.py
├── ml/                       # Pipeline de Machine Learning
│   ├── data_utils.py        # Geração de dados sintéticos
│   ├── model_utils.py       # Utilidades do modelo
│   └── train.py             # Script de treino
├── tests/                    # Testes com pytest
│   ├── conftest.py          # Fixtures e configuração
│   ├── test_saude.py        # Testes de health check
│   └── test_contratos.py    # Testes de contrato
├── .github/workflows/        # GitHub Actions
│   └── ci.yml               # Pipeline CI/CD
├── .env                      # Variáveis de ambiente
├── requirements.txt          # Dependências Python
├── Dockerfile               # Containerização
├── pytest.ini               # Configuração do pytest
└── README.md               # Este arquivo
```

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- pip ou uv

### Instalação

```bash
# Clonar o repositório
git clone <repo-url>
cd bella-tavola

# Instalar dependências
pip install -r requirements.txt
```

### Executar a API

```bash
# Desenvolvimento
uvicorn src.main:app --reload

# Produção
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`

Documentação Swagger: `http://localhost:8000/docs`

### Rodar Testes

```bash
# Todos os testes
pytest tests/ -v

# Apenas testes smoke (rápidos)
pytest tests/ -m smoke -v

# Testes com cobertura
pytest tests/ --cov=src
```

## 🐳 Docker

```bash
# Build
docker build -t bella-tavola .

# Run
docker run -p 8000:8000 bella-tavola
```

## 📚 Endpoints Principais

### Pratos
- `GET /pratos` - Listar todos os pratos
- `GET /pratos/{id}` - Obter prato específico
- `POST /pratos` - Criar novo prato

### Bebidas
- `GET /bebidas` - Listar todas as bebidas
- `GET /bebidas/{id}` - Obter bebida específica
- `POST /bebidas` - Criar nova bebida

### Pedidos
- `POST /pedidos` - Criar novo pedido

### Reservas
- `GET /reservas` - Listar reservas
- `POST /reservas` - Criar nova reserva
- `DELETE /reservas/{id}` - Cancelar reserva

### Health Check
- `GET /health` - Status da API
- `GET /` - Informações da API

## 🤖 Machine Learning

O projeto inclui um pipeline de ML para detecção de fraude:

```bash
# Gerar dados sintéticos e treinar modelo
cd ml
python train.py
```

## 🔧 Variáveis de Ambiente

Configure em `.env`:

```
APP_NAME=Bella Tavola API
APP_VERSION=1.0.0
DEBUG=true
MAX_MESAS=15
MAX_PESSOAS_POR_MESA=8
HF_TOKEN=<seu-token-huggingface>
```

## 📦 Dependências Principais

- **fastapi** - Framework web
- **pydantic** - Validação de dados
- **scikit-learn** - Machine Learning
- **pytest** - Testes
- **huggingface_hub** - Registro de modelos

## 🔄 CI/CD

O projeto utiliza GitHub Actions com:
1. **Qualidade**: Formatação (black), imports (autoflake), testes smoke
2. **Integração**: Testes de integração com cache do HuggingFace

## 👨‍💻 Desenvolvimento

### Code Style
```bash
black .
autoflake --remove-all-unused-imports -r .
```

### Adicionar Novos Endpoints

1. Criar modelo em `src/models/`
2. Criar router em `src/routers/`
3. Incluir router em `src/main.py`
4. Adicionar testes em `tests/`

## 📄 Licença

MIT
