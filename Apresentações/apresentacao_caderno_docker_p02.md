# 🐳 Apresentação — Caderno 05-p02: Docker para MLOps (Parte 2)

## Bella Tavola 🍝 — Configurando, orquestrando e refinando

> **Objetivo do caderno:** Resolver os dois problemas deixados em aberto na Parte 1 (token e persistência), orquestrar um sistema multi-serviço com Docker Compose (API + PostgreSQL + Nginx) e refinar a imagem para produção com `.dockerignore`, usuário não-root e multi-stage build.

---

## 🎬 Roteiro de Apresentação

1. **Introdução** — onde paramos na Parte 1 e o que falta resolver
2. **Setup** — confirmar que e05-p01 está completo
3. **Bloco 10 — Variáveis de ambiente** (`HF_TOKEN`) e volumes
4. **Bloco 11 — Docker Compose** — API + PostgreSQL + Nginx
5. **Bloco 12 — Boas práticas** — `.dockerignore`, não-root, multi-stage
6. **Conclusão** — o sistema refinado e a ponte para a Parte 3 (CI)

---

## 🛠️ Setup do Ambiente e Pré-requisitos

Antes de começar, confirme que **e05-p01 está completo**:

```bash
# Na raiz do projeto Bella Tavola

# 1. O Dockerfile existe e builda?
docker build -t bella-tavola:v1 .
# Esperado: Successfully built (ou: writing image sha256:...)

# 2. A API responde dentro do contêiner?
docker run -p 8000:8000 --rm bella-tavola:v1 &
sleep 3
curl http://localhost:8000/
# Esperado: {"restaurante": "Bella Tavola", ...}
```

> Os Blocos 10, 11 e 12 constroem **diretamente** sobre o `Dockerfile` da Parte 1. Se qualquer item falhar, volte para e05-p01 antes de continuar.

---

# 🔵 BLOCO 10 — Variáveis de ambiente e volumes

## Visual: Ciclo de vida — com e sem volume

```
┌─────────────────────────────────────────────────────────────┐
│ SEM VOLUME (-v) — Dados efêmeros                            │
├─────────────────────────────────────────────────────────────┤
│ docker run ... bella-tavola:v1                              │
│   ↓                                                          │
│ Contêiner 1 rodando                                         │
│   ├── /app/banco.db (dentro do contêiner)                   │
│   └── Criado 2 pratos                                       │
│   ↓ docker rm (ou stop + start sem volume)                  │
│ Contêiner 1 APAGADO ← banco.db também desaparece ❌        │
│                                                              │
│ docker run ... bella-tavola:v1                              │
│   ↓                                                          │
│ Contêiner 2 rodando (novo, vazio)                           │
│   ├── /app/banco.db (novo e vazio)                          │
│   └── 0 pratos (começou do zero)                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ COM NAMED VOLUME (-v bella-dados:/app/data) — Persistência  │
├─────────────────────────────────────────────────────────────┤
│ docker run -v bella-dados:/app/data bella-tavola:v1        │
│   ↓                                                          │
│ Contêiner 1 rodando                                         │
│   ├── /app/data/banco.db → montado de bella-dados           │
│   └── Criado 2 pratos                                       │
│   ↓ docker rm                                               │
│ Contêiner 1 APAGADO ← banco.db continua em bella-dados ✅  │
│                                                              │
│ Volume bella-dados (Docker storage)                         │
│   └── /app/data/banco.db (persiste)                         │
│                                                              │
│ docker run -v bella-dados:/app/data bella-tavola:v1        │
│   ↓                                                          │
│ Contêiner 2 rodando (novo, conectado ao mesmo volume)       │
│   ├── /app/data/banco.db (mesmo arquivo)                    │
│   └── 2 pratos (dados sobreviveram!)                        │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 Conceitos-chave do Bloco 10

- **Três formas de passar variáveis:** `-e CHAVE=valor` (pontual), `--env-file .env` (várias), `ENV` no Dockerfile (padrões **não sensíveis**).
- **Regra de ouro:** nunca use `ENV` para secrets — o valor fica gravado na imagem e aparece em `docker history`. O `BaseSettings` do Pydantic (Caderno e02) já lê variáveis de ambiente automaticamente.
- **Contêineres são efêmeros → volumes persistem dados** independentemente do ciclo de vida do contêiner:
  - **Named volume** (`-v bella-dados:/app/data`) → gerenciado pelo Docker, para dados de produção (banco, uploads)
  - **Bind mount** (`-v $(pwd):/app`) → espelha um diretório seu, para desenvolvimento (live reload)
- **`docker volume rm` apaga dados permanentemente** — sem lixeira, sem undo.

---

## ✏️ Exercício 10.1 — Passando o HF_TOKEN para o contêiner

**O que o exercício pede:** Rodar a API sem token (observar o erro em `/ml/predict`), depois com `-e HF_TOKEN=...` e com `--env-file .env`, confirmando que a predição passa a funcionar.

**Função do exercício:**
- Aplicar em contêiner o mesmo cuidado com secrets da Semana 3
- Confirmar que o `.env` nunca deve ser commitado

### Resolução - Demonstração prática

**SEM token:**
```bash
$ docker run -p 8000:8000 --rm bella-tavola:v1 &
sleep 3

$ curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"valor_transacao": 150.0, "hora_transacao": 14, ...}'

# Resposta esperada:
# HTTP/1.1 500 Internal Server Error
# {"detail":"HTTPError: 401 Client Error: Unauthorized"}

# Ou nos logs do contêiner:
# huggingface_hub.utils._errors.RepositoryNotFoundError
# requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**COM token via `-e`:**
```bash
$ docker run -p 8000:8000 --rm -e HF_TOKEN=hf_seu_token_aqui bella-tavola:v1 &
sleep 3

$ curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"valor_transacao": 150.0, "hora_transacao": 14, ...}'

# Resposta esperada:
# HTTP/1.1 200 OK
# {"prediction": 0, "probability": 0.12, "label": "legítimo", ...}
```

**COM token via `--env-file`:**
```bash
$ cat .env | grep HF_TOKEN
HF_TOKEN=hf_seu_token_aqui

$ docker run -p 8000:8000 --rm --env-file .env bella-tavola:v1 &
sleep 3

$ curl -X POST http://localhost:8000/ml/predict ...
# Mesma resposta de sucesso ✅
```

**Por que `.env` nunca no Git:**
```text
Contém HF_TOKEN (e senhas de banco, API keys).
Quem clonar o repositório teria acesso imediato.
Se o repositório for público: o mundo todo tem acesso.
O token do Hugging Face dá acesso de ESCRITA ao seu Hub —
podendo deletar ou sobrescrever seus modelos publicados.

Deve estar no .gitignore (já está) e no .dockerignore (Bloco 12).
```

**Pontos para falar no vídeo:**
- O endpoint `/ml/predict` é o **teste vivo** do token — é exatamente onde a Parte 1 falhava
- Mesma disciplina de secrets da Semana 3, agora no mundo dos contêineres

---

## ✏️ Exercício 10.2 — Persistindo dados com volume

**O que o exercício pede:** Criar registros via API, **destruir** o contêiner, subir um novo com o **mesmo** named volume e verificar que os dados sobreviveram.

**Função do exercício:**
- Provar que o volume vive independentemente do contêiner
- Fechar o problema da efemeridade levantado no Bloco 8

### Resolução

```text
Os dados persistem: o contêiner foi destruído, mas o volume continuou no
Docker storage; o novo contêiner se conectou a ele e achou os dados.

Sem -v: o SQLite ficaria dentro do contêiner; docker rm apagaria tudo.
Cada novo contêiner começaria com banco vazio.

docker volume ls mostra o volume mesmo sem contêiner — volumes são
cidadãos de primeira classe. docker volume rm bella-dados apaga os
dados PERMANENTEMENTE. (docker compose down -v faz isso para todos.)
```

**Pontos para falar no vídeo:**
- Demonstração ao vivo é poderosa: criar prato → destruir contêiner → recriar → o prato ainda lá
- Isso é o que permite **atualizar a imagem da app sem perder os dados** do banco

---

## ✏️ Exercício 10.3 — Bind mount para desenvolvimento

**O que o exercício pede:** Subir a API com `-v $(pwd):/app` e `uvicorn --reload`, alterar uma rota e ver o uvicorn recarregar **sem rebuildar**.

**Função do exercício:**
- Conhecer o fluxo de desenvolvimento com live reload no contêiner
- Entender por que bind mount **não substitui** o `COPY . .`

### Resolução

```text
O uvicorn recarrega sozinho ao salvar o arquivo — sem rebuild.

Bind mount NÃO substitui COPY . . porque com ele o código existe só na
sua máquina. A imagem em si não tem o código novo — tem o do build.
Em produção não existe o seu diretório local; só a imagem.

Bind mount em produção é problemático: depende do caminho exato,
qualquer mudança no diretório afeta o contêiner ao vivo, não é
reproduzível e derrota o propósito do contêiner.
→ Bind mount = ferramenta de dev. COPY . . = produção.
```

**Pontos para falar no vídeo:**
- A síntese: **bind mount para desenvolver, `COPY . .` para entregar**
- Live reload no contêiner dá o melhor dos dois mundos durante o dev sem abrir mão do isolamento

---

## ✏️ Exercício 10.4 — Inspecionando volumes

**O que o exercício pede:** Usar `docker volume ls` e `docker volume inspect bella-dados`, achar o `Mountpoint` e pensar em backup e nos riscos do `volume prune`.

**Função do exercício:**
- Saber onde os dados vivem fisicamente e como fazer backup com segurança

### Resolução

```text
O Mountpoint aponta para /var/lib/docker/volumes/.../_data. No macOS/
Windows isso fica dentro da VM do Docker Desktop — não acessível pelo
Finder/Explorer.

Backup confiável via contêiner auxiliar:
  docker run --rm -v bella-dados:/data alpine tar czf - /data > backup.tar.gz

docker volume prune ainda é perigoso: remove volumes sem contêiner
ATIVO — inclusive o de um banco cujo contêiner está só parado (não
removido). Resultado: perda de dados sem querer.
```

**Pontos para falar no vídeo:**
- "Onde meus dados estão de verdade?" tem resposta concreta — e em Mac/Windows ela está escondida numa VM
- O padrão do contêiner auxiliar para backup é um truque que vale levar para o trabalho

---

# 🔵 BLOCO 11 — Docker Compose: orquestrando múltiplos serviços

## Visual: Arquitetura do Compose

```
┌─────────────────────────────────────────────────────────────┐
│ COMPOSIÇÃO: API + PostgreSQL + Nginx                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Seu computador (host)                                      │
│  ├── localhost:80   ←─ porta 80 exposta (Nginx)            │
│  └── localhost:8000 ←─ NOT exposta (API está protegida)    │
│                                                              │
│  Docker Compose (rede privada: bella-tavola_default)       │
│  │                                                          │
│  ├─ nginx:alpine        (porta 80 ↔ :80)                   │
│  │  └─ proxy_pass http://api:8000                          │
│  │                   (resolve via DNS interno do Compose)   │
│  │                                                          │
│  ├─ api (bella-tavola:v3) (porta 8000, NOT exposta)        │
│  │  └─ DATABASE_URL=postgresql://...@db:5432/...           │
│  │                   (também resolve via DNS)               │
│  │  └─ depends_on: db (condition: service_healthy)        │
│  │                                                          │
│  └─ db (postgres:15)    (porta 5432, NOT exposta)          │
│     └─ healthcheck: pg_isready (permite service_healthy)  │
│     └─ volume: bella-pg-data (Docker storage)             │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Fluxo de requisição:
Usuário → curl http://localhost:80
         ↓
    Nginx (escuta na porta 80)
         ↓ (DNS resolve 'api' para o IP interno)
    API (uvicorn rodando em 0.0.0.0:8000)
         ↓ (DNS resolve 'db' para o IP interno)
    PostgreSQL (rodando em :5432)

Nenhuma porta é acessível diretamente do seu computador,
exceto a porta 80 do Nginx (o "ponto de entrada").
```

## 🧠 Conceitos-chave do Bloco 11

- **O Compose troca N comandos `docker run` longos** (rede manual, flags, três terminais) por **um arquivo declarativo** + `docker compose up` / `down`.
- **Mesma sintaxe YAML do GitHub Actions.** `services:` → cada serviço é um contêiner; o nome do serviço vira o **hostname** na rede interna.
- **`build:` vs `image:`** — `build: .` constrói do Dockerfile local (sua API); `image: postgres:15` usa imagem pronta do registry (banco, proxy).
- **Rede interna + DNS:** dentro do Compose, a API acessa o banco em `...@db:5432/...` e o Nginx acessa a API em `http://api:8000`. **`localhost` dentro de um contêiner é o próprio contêiner** — fonte do erro mais comum.
- **`depends_on` garante ordem de início, não prontidão.** Para esperar o banco aceitar conexões: `healthcheck` + `condition: service_healthy`.
- **`down` preserva volumes; `down -v` apaga volumes** (dados perdidos).

---

## ✏️ Exercício 11.1 — Compose mínimo: só a API

**O que o exercício pede:** Escrever o primeiro `docker-compose.yml` (serviço único `api` com `build`, `ports`, `env_file`, `volumes`), subir com `docker compose up` e comparar com o `docker run` equivalente.

**Função do exercício:**
- Traduzir o que já se sabe de `docker run` para a forma declarativa

### Resolução

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - bella-dados:/app/data

volumes:
  bella-dados:
```

```text
Equivalente em docker run:
  docker run -p 8000:8000 --env-file .env -v bella-dados:/app/data bella-tavola:v1

O que o Compose faz a mais: cria rede privada automática, nomeia o
contêiner, remove contêiner+rede no down (preservando volumes),
gerencia dependências e permite escalar (--scale api=3).
```

**Pontos para falar no vídeo:**
- O ganho não é "menos digitação" e sim **declaratividade**: o arquivo É a documentação do sistema
- `down` preserva o volume — intencional: parar serviços não é apagar dados

---

## ✏️ Exercício 11.2 — Adicionando PostgreSQL

**O que o exercício pede:** Adicionar o serviço `db` (postgres:15) e, **de propósito**, configurar a `DATABASE_URL` com `localhost` para observar a falha, antes de corrigir para o hostname `db`.

**Função do exercício:**
- Internalizar a rede do Compose causando o erro mais comum de propósito

### Resolução - Checkpoints de falha esperada

**Passo 1: Causar o erro COM `localhost` (de propósito)**

```yaml
# docker-compose.yml com BUG (para demonstração)
services:
  api:
    environment:
      DATABASE_URL: postgresql://bella:secreta@localhost:5432/bellatavolada
      #                                        ↑ ERRADO — localhost é o próprio contêiner
```

```bash
$ docker compose up -d
$ sleep 5
$ docker compose logs api

# Output nos logs:
# sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)
# connection to server at "localhost" (127.0.0.1), port 5432 failed:
# Connection refused
# ou:
# asyncpg.exceptions.ConnectionRefusedError: Connection refused
```

```bash
$ docker compose logs db
# Você verá:
# LOG: database system is ready to accept connections
# ← O banco SUBIU normalmente — o problema não é lá!
```

**Por que falha:** Dentro do contêiner da API, `localhost` (127.0.0.1) = **o próprio contêiner da API**. Não há PostgreSQL ali. É como ligar para você mesmo esperando que outra pessoa atenda.

**Passo 2: Corrigir para usar o nome do serviço**

```yaml
# docker-compose.yml CORRETO
services:
  api:
    environment:
      DATABASE_URL: postgresql://bella:secreta@db:5432/bellatavolada
      #                                       ↑ nome do serviço = hostname
```

```bash
$ docker compose down
$ docker compose up -d
$ sleep 5
$ docker compose logs api

# Agora você vê:
# INFO: Application startup complete.
# ← API iniciou com sucesso, conectada ao banco!
```

**Por que funciona:** O Compose cria um **servidor DNS interno** que mapeia nomes de serviços para os IPs internos dos contêineres. `db` → IP do contêiner do PostgreSQL na rede Compose.

| Contexto | `localhost` aponta para | Resultado |
|----------|---|---|
| Seu computador | Seu computador | ✅ funciona |
| Dentro do contêiner da API | O próprio contêiner | ❌ não há DB aqui |
| Na rede do Compose | DNS resolve `db` para o IP do PostgreSQL | ✅ funciona |

**Pontos para falar no vídeo:**
- A analogia: *"é como ligar para você mesmo esperando que outra pessoa atenda"*
- Esse é **o** erro de quem migra para Compose — vê-lo acontecer fixa a mudança de modelo mental: serviço = hostname

---

## ✏️ Exercício 11.3 — Adicionando Nginx como proxy reverso

**O que o exercício pede:** Criar `nginx.conf`, adicionar o serviço `nginx` (porta 80), **remover** o `ports` da API e confirmar que a API responde via `http://localhost` (porta 80) e **não** mais na 8000.

**Função do exercício:**
- Entender o papel do proxy reverso e por que o uvicorn não deve ser o ponto de entrada público

### Resolução

```nginx
server {
    listen 80;
    location / {
        proxy_pass http://api:8000;   # 'api' = serviço na rede Compose
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```text
Antes:  Usuário → porta 8000 → uvicorn
Depois: Usuário → porta 80 → Nginx → porta 8000 → uvicorn

O nome 'api' no proxy_pass é resolvido pelo DNS interno do Compose.
Em produção, o nginx.conf também faria: SSL/TLS, rate limiting, gzip,
headers de segurança, cache e timeouts (ex.: /ml/predict é lento).
```

**Pontos para falar no vídeo:**
- O Nginx é a "recepção" do sistema: SSL, compressão, rate limiting; a API fica numa porta interna, protegida
- Removendo o `ports` da API, ela deixa de ser acessível direto — só via Nginx. É o desenho de produção.

---

## ✏️ Exercício 11.4 — Desafio: healthcheck e ordem de inicialização 🎯

**O que o exercício pede:** Adicionar `healthcheck` ao `db` (com `pg_isready`) e mudar o `depends_on` da API para `condition: service_healthy`.

**Função do exercício:**
- Resolver de verdade a race condition que o `depends_on` sozinho não cobre

### Resolução

```yaml
db:
  image: postgres:15
  # environment / volumes ...
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U bella -d bellatavolada"]
    interval: 5s
    timeout: 5s
    retries: 5
    start_period: 10s

api:
  depends_on:
    db:
      condition: service_healthy
```

```text
depends_on sozinho garante que o banco INICIOU, não que está PRONTO.
O Postgres leva alguns segundos após subir o processo. Com
condition: service_healthy, a API só inicia depois do healthcheck passar
— eliminando a necessidade de lógica de retry na aplicação.
```

**Pontos para falar no vídeo:**
- O ponto fino: **"iniciou" ≠ "pronto para conexões"** — é a causa de falhas intermitentes na subida
- `healthcheck` é a solução robusta; retry na app é o paliativo

---

# 🔵 BLOCO 12 — Boas práticas: segurança e eficiência

## Visual: Multi-stage build

```
┌──────────────────────────────────────────────────────────┐
│ DOCKERFILE SIMPLES (Bloco 9 / Parte 1)                   │
├──────────────────────────────────────────────────────────┤
│ FROM python:3.11-slim                                    │
│ COPY requirements.txt .                                  │
│ RUN pip install --no-cache-dir -r requirements.txt       │
│ COPY . .                                                 │
│                                                          │
│ Imagem resultante: ~1.1–1.3GB                            │
│   ├── Python 3.11                                        │
│   ├── pip + setuptools                                   │
│   ├── numpy, scikit-learn, etc (compilados)             │
│   ├── gcc, headers de desenvolvimento (desnecessários!)  │
│   ├── Cache de downloads de pip (desnecessário!)        │
│   └── Seu código Python                                  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ MULTI-STAGE BUILD (Bloco 12 / Parte 2)                   │
├──────────────────────────────────────────────────────────┤
│ ESTÁGIO 1: BUILDER                                       │
│ ─────────────────────────────────────────────────────    │
│ FROM python:3.11-slim AS builder                         │
│ COPY requirements.txt .                                  │
│ RUN pip install --prefix=/install -r requirements.txt    │
│                                                          │
│ Contém: Python, gcc, headers, cache (TEMPORÁRIO)         │
│ Tamanho: ~2GB (descartado no final)                      │
│                                                          │
│ ESTÁGIO 2: FINAL (imagem entregável)                     │
│ ──────────────────────────────────────────────────────   │
│ FROM python:3.11-slim                                    │
│ COPY --from=builder /install /usr/local   ← copia apenas │
│ COPY . .                                   ← pacotes!    │
│                                                          │
│ Imagem resultante: ~700–900MB                            │
│   ├── Python 3.11                                        │
│   ├── pip + setuptools                                   │
│   ├── numpy, scikit-learn, etc (compilados) ← mantém    │
│   └── Seu código Python                                  │
│                                                          │
│ ✅ gcc, headers, cache foram descartados no builder!    │
│ ✅ Redução: 30–40% (pura eliminação de ferramentas)     │
└──────────────────────────────────────────────────────────┘
```

## 🧠 Conceitos-chave do Bloco 12

- **`.dockerignore`** (mesmo formato do `.gitignore`): impede que `__pycache__`, `.git`, `.env`, `venv`, `*.pkl`, `tests/`, `*.ipynb` entrem na imagem. **Benefício principal não é tamanho — é segurança** (o `.env` fora da imagem), velocidade de build e cache.
- **Usuário não-root:** por padrão o processo roda como `root`. Criar `appuser` e usar `USER appuser` aplica o **princípio do menor privilégio**. O `USER` precisa vir **depois** do `pip install` (que exige root) e do `chown -R`.
- **Multi-stage build:** estágio `builder` instala as dependências (precisa de compiladores); estágio final copia só os pacotes prontos (`COPY --from=builder /install /usr/local`). Reduz a imagem em ~30–40% ao descartar compiladores e cache de build.

---

## ✏️ Exercício 12.1 — Adicionando `.dockerignore`

**O que o exercício pede:** Medir o tamanho/conteúdo da imagem, criar o `.dockerignore`, rebuildar e confirmar que o `.env` não está mais na imagem.

**Função do exercício:**
- Reduzir o build context, proteger secrets e limpar a imagem

### Resolução

```text
# .dockerignore (essencial)
__pycache__
*.pyc
.git
.env
*.env
env_ci_test/
venv/
*.pkl
tests/
*.ipynb
.dockerignore
```

```text
A redução de TAMANHO costuma ser modesta — o peso está nos PACOTES do
pip (~800MB–1.2GB), não no código. O ganho real é:
1. SEGURANÇA: .env não entra na imagem (se vazar, secrets não vazam)
2. BUILD mais rápido (contexto menor)
3. CACHE não invalidado por arquivos ignorados
4. Imagem de produção só com o necessário
Confirmação: docker run --rm bella-tavola:v2 find /app -name '.env' → vazio
```

**Pontos para falar no vídeo:**
- O benefício que importa é **segurança**, não bytes — desmistificar a expectativa de "imagem muito menor"
- A redução de tamanho de verdade vem do multi-stage (12.3)

---

## ✏️ Exercício 12.2 — Usuário não-root

**O que o exercício pede:** Confirmar que a imagem roda como `root`, adicionar criação de `appuser` + `chown` + `USER appuser`, rebuildar e validar com `whoami` que agora roda como `appuser`.

**Função do exercício:**
- Aplicar o princípio do menor privilégio e entender a **ordem** das instruções

### Resolução

```dockerfile
COPY . .
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser
```

```text
USER vem DEPOIS do pip install porque a instalação grava em
/usr/local/.../site-packages, que exige root. Se USER viesse antes:
  PermissionError: [Errno 13] Permission denied: '/usr/local/lib/...'

Ordem correta: instalar (root) → copiar código (root) → criar usuário →
chown → USER → CMD roda como não-root.
Se a API cria arquivos em runtime: mkdir -p /app/data && chown antes do USER.
```

**Pontos para falar no vídeo:**
- O "porquê da ordem" é o coração do exercício: privilégio para instalar, depois rebaixa para rodar
- Menor privilégio: se um atacante explorar a API, ele cai como `appuser`, não como `root`

---

## ✏️ Exercício 12.3 — Multi-stage build

**O que o exercício pede:** Refatorar o Dockerfile em dois estágios (`builder` + final), rebuildar como `v3` e comparar o tamanho com `v2`.

**Função do exercício:**
- Separar build de runtime para enxugar a imagem final

### Resolução - Código e comparação real

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Tamanhos reais antes e depois:**
```bash
$ docker images bella-tavola
REPOSITORY      TAG    IMAGE ID       SIZE
bella-tavola    v1     e52d616058ff   1.1GB   ← Bloco 9 (simples)
bella-tavola    v2     a1f3e7c0d2b4   1.0GB   ← Bloco 12.1 (.dockerignore)
bella-tavola    v3     f7c4b2e1d9a6   750MB   ← Bloco 12.3 (multi-stage)

# Redução:
# v1 → v3: 1.1GB → 750MB = 32% menor
# v2 → v3: 1.0GB → 750MB = 25% menor
```

```text
Redução típica em ML: v2 ~1.1–1.3GB → v3 ~700–900MB (30–40% menos).

Eliminado: compiladores (gcc), headers de dev, intermediários de
compilação e cache do pip — nada disso é necessário para RODAR.

A redução não é maior porque os .so compilados (numpy, scikit-learn)
são grandes e precisam ficar na imagem final.
```

**Pontos para falar no vídeo:**
- A ideia central: **o que é preciso para instalar ≠ o que é preciso para rodar**
- O estágio `builder` é um andaime — usado e descartado
- A economia é **32% de redução de tamanho** — significante para CI/CD!

---

## ✏️ Exercício 12.4 — Desafio: análise de layers com `docker history` 🎯

**O que o exercício pede:** Inspecionar `v1` e `v3` com `docker history`, identificar a maior layer e (bônus) usar `dive`.

**Função do exercício:**
- Aprender a diagnosticar o que ocupa espaço numa imagem

### Resolução

```text
Em v1, a maior layer é o RUN pip install (scikit-learn + numpy + deps).
Em v3, a layer do pip install do builder NÃO aparece — docker history só
mostra as layers da imagem FINAL; o builder foi descartado. O que aparece
é o COPY --from=builder (tamanho similar, sem os intermediários).

A maior layer de v3 segue sendo os pacotes instalados. Para reduzir mais:
enxugar requirements.txt, usar versões mais leves.

'dive' mostra o que docker history não mostra: arquivos individuais por
layer, arquivos desperdiçados (add numa layer, removidos em outra) e a
% de conteúdo útil da imagem.
```

**Pontos para falar no vídeo:**
- `docker history` mostra **tamanho por instrução**; `dive` mostra **arquivos por layer** — ferramentas complementares
- O fato de a layer do builder sumir em v3 é a prova visual de que multi-stage funciona

---

# 📋 Checklist de pré-requisitos para e05-p03

Antes de avançar para a **Parte 3 (Pipeline de CI)**, confirme **todos** os itens abaixo. A Parte 3 depende completamente destes.

```bash
# 1. Docker Compose funciona completo
$ docker compose up -d
$ docker compose ps
# Saída: 3 serviços rodando (api, db, nginx)

# 2. API responde via Nginx (porta 80, não 8000)
$ curl http://localhost/
{"restaurante":"Bella Tavola",...}  ✅

$ curl http://localhost:8000/
# curl: (7) Failed to connect — porta 8000 NÃO está exposta ✅

# 3. /ml/predict funciona com token
$ curl -X POST http://localhost/ml/predict \
  -H "Content-Type: application/json" \
  -d '{"valor_transacao": 150.0, "hora_transacao": 14, ...}'
{"prediction": 0, "probability": 0.12, ...}  ✅

# 4. Dados persistem
$ docker compose down    # sem -v!
$ docker compose up -d
$ curl http://localhost/pratos
# Os pratos criados antes ainda estão lá ✅

# 5. Dockerfile usa usuário não-root
$ docker run --rm bella-tavola:v3 whoami
appuser  ✅ (não root)

# 6. Arquivo .env NÃO está na imagem
$ docker run --rm bella-tavola:v3 find /app -name '.env'
# Nenhuma saída ✅

# 7. Criar conta no Docker Hub (se não tem)
# Acesse: https://hub.docker.com/signup

# 8. Criar repositório 'bella-tavola' no Docker Hub
# No site: Create Repository → Nome: bella-tavola → Public

# 9. Fazer login no Docker
$ docker login
# Username: seu-usuario
# Password: seu-token-hub

# 10. Pipeline de CI da Semana 3 está verde
# Verifique: https://github.com/seu-usuario/bella-tavola/actions
# Commit e veja o workflow passar (Build, Test, etc)
```

**Se qualquer item falhar, resolva antes de começar e05-p03.** Não pule essas etapas — a Parte 3 é puramente CI/CD e depende de tudo estar funcionando localmente.

---

# 🗺️ Mapa do que foi construído (Parte 2)

```
e05-p02  ──►  .dockerignore        →  protege secrets, limpa a imagem
              docker-compose.yml   →  orquestra API + PostgreSQL + Nginx
              nginx.conf           →  proxy reverso na porta 80
              Dockerfile (refat.)  →  multi-stage build + usuário não-root
```

---

# ✅ Checklist de Competências — e05-p02

**Bloco 10 — Variáveis de ambiente e volumes**
- ✅ Passar o `HF_TOKEN` ao contêiner sem hardcodá-lo na imagem
- ✅ `/ml/predict` funciona dentro do contêiner com o token
- ✅ Criar named volume e verificar persistência após recriar o contêiner
- ✅ Diferenciar bind mount de named volume e saber quando usar cada um

**Bloco 11 — Docker Compose**
- ✅ Escrever um `docker-compose.yml` com múltiplos serviços
- ✅ Entender `build:` vs `image:`
- ✅ Comunicação entre serviços pelo nome (hostname) e `healthcheck`
- ✅ Diferenciar `down` de `down -v`; API respondendo via Nginx (porta 80)

**Bloco 12 — Boas práticas**
- ✅ `.dockerignore` criado e `.env` fora da imagem
- ✅ A API roda como usuário não-root
- ✅ Multi-stage build implementado e tamanho reduzido

---

# 🎤 Conclusão para o Vídeo (Parte 2)

> "Nesta segunda parte, a imagem da Bella Tavola deixou de ser 'um contêiner solto' e virou um **sistema**. Primeiro fechei os dois problemas que a Parte 1 deixou em aberto: passei o `HF_TOKEN` ao contêiner sem hardcodá-lo (com a mesma disciplina de secrets da Semana 3) e persisti os dados com **volumes** — provando ao vivo que o dado sobrevive à destruição do contêiner.
>
> No Bloco 11, troquei uma pilha de comandos `docker run` por um `docker-compose.yml` declarativo, orquestrando API + PostgreSQL + Nginx. O aprendizado que mais marca é o erro que cometi de propósito: dentro do Compose, **`localhost` é o próprio contêiner** — serviços se acham pelo **nome do serviço** como hostname. E o `healthcheck` resolveu a diferença sutil entre o banco *iniciar* e estar *pronto para conexões*.
>
> O Bloco 12 refinou a imagem com três práticas que resolvem problemas concretos: o `.dockerignore` mantém o `.env` fora da imagem (segurança), o **usuário não-root** aplica o menor privilégio, e o **multi-stage build** descarta os compiladores que só servem para instalar — cortando a imagem em 30 a 40%.
>
> O resultado é um sistema seguro, enxuto e reproduzível. Mas ele ainda vive só na minha máquina. Na Parte 3, essa imagem entra no pipeline de CI e passa a ser publicada automaticamente."
