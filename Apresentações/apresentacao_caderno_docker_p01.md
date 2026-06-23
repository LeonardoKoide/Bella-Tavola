# 🐳 Apresentação — Caderno 05-p01: Docker para MLOps (Parte 1)

## Bella Tavola 🍝 — Construindo e rodando sua primeira imagem

> **Objetivo do caderno:** Conectar Docker ao problema que você já viveu — a máquina limpa do CI — e sair com a API Bella Tavola rodando dentro de um contêiner local reproduzível. Cobre os fundamentos: por que contêineres existem, o ciclo de vida básico e o primeiro `Dockerfile` real.

---

## 🎬 Roteiro de Apresentação

1. **Introdução** — quem sou eu e o que vou apresentar
2. **Setup** — pré-requisitos e a ponte com o caderno anterior (CI verde)
3. **Bloco 7 — Por que Docker?** O limite do `venv` que você já conhece
4. **Bloco 8 — Primeiros comandos** e o ciclo de vida do contêiner
5. **Bloco 9 — O `Dockerfile`** da Bella Tavola e o cache de build
6. **Conclusão** — a API em contêiner e o que ficou em aberto para a Parte 2

---

## 🛠️ Setup do Ambiente e Pré-requisitos

- **API Bella Tavola** funcionando localmente (Caderno 02 — FastAPI)
- **Modelo publicado no Hugging Face Hub** e `load_model` funcionando (Caderno 03 — ML)
- **Pipeline de CI da Semana 3 verde** no GitHub Actions (Caderno 04)
- **Docker instalado** (Docker Desktop no Windows/macOS, Docker Engine no Linux)

### Verificação rápida antes de começar

```bash
# 1. A API sobe sem erro
$ uvicorn src.main:app --reload
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
# ✅ Se você vir "Application startup complete", pode continuar

# 2. A API responde
$ curl http://localhost:8000/
{"restaurante":"Bella Tavola","versao":"1.0.0"}
# ✅ JSON retorna normalmente

# 3. Docker está instalado
$ docker --version
Docker version 29.5.3, build d1c06ef
# ✅ Versão 25+ é o que você precisa
```

**Se qualquer um falhar, resolva antes de continuar.** Neste caderno, o Docker reproduz seu ambiente — ele não conserta um ambiente quebrado.

> Mesma filosofia da Semana 3: **se não funciona localmente, não vai funcionar no contêiner.** O Docker reproduz seu ambiente — ele não conserta um ambiente quebrado. Resolva qualquer falha antes de containerizar.

---

# 🔵 BLOCO 7 — Por que Docker? O problema que você já conhece

## Visual: O limite do `venv`

```
┌─────────────────────────────────────────────────────┐
│  O que você esperava (no seu computador)            │
├─────────────────────────────────────────────────────┤
│ Python 3.11 ✓                                      │
│ fastapi, scikit-learn, numpy ✓                     │
│ Variável HF_TOKEN = "seu-token" ✓                │
│ Arquivo .env ✓                                     │
│ Porta 8000 disponível ✓                            │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│  O que a máquina limpa de CI tinha (Semana 3)       │
├─────────────────────────────────────────────────────┤
│ Python 3.9 (você tem 3.11)                         │
│ fastapi, scikit-learn, numpy ✓                     │
│ Variável HF_TOKEN = ??? (arquivo .env não existe) │
│ Arquivo .env (não commitado por segurança)        │
│ Porta 8000 disponível ✓                            │
└─────────────────────────────────────────────────────┘
         ↓ FALHA!

┌─────────────────────────────────────────────────────┐
│  O que o contêiner oferece (este caderno)          │
├─────────────────────────────────────────────────────┤
│ Python 3.11 ✓                                      │
│ fastapi, scikit-learn, numpy ✓                     │
│ Variável HF_TOKEN = "seu-token" ✓                │
│ Arquivo .env ✓                                     │
│ SO Debian mínimo com tudo pré-configurado ✓      │
│ Porta 8000 mapeada corretamente ✓                 │
│ = Reproduzível em qualquer lugar                   │
└─────────────────────────────────────────────────────┘
```

## 🧠 Conceitos-chave do Bloco 7

- **O `venv` isola só pacotes Python** — e nada além disso. Não isola a versão do Python, bibliotecas do sistema (`libgomp`, `libssl`), binários (`curl`, `git`), variáveis de ambiente, versão do SO, nem rede/portas.
- **O contêiner isola tudo:** SO, libs do sistema, binários, variáveis, processos e rede. É uma unidade que carrega o ambiente completo.
- **Não substitui o `venv`** — em desenvolvimento local o `venv` continua certo. O contêiner resolve um problema diferente: *"como garantir que produção é idêntico a desenvolvimento."*
- **Imagem vs. contêiner** (a distinção que mais confunde no início):
  - **Imagem** = receita / classe Python → definição estática e imutável, não consome recursos em repouso
  - **Contêiner** = bolo assado / instância → imagem em execução, consome CPU/memória, pode ser criado/parado/removido
- **Docker Hub** = registry público de imagens, análogo ao PyPI. `FROM python:3.11-slim` baixa a imagem oficial de lá.

### A frase para fixar

```
Ambiente virtual:  seu código + pacotes Python                →  roda no SO do host
Contêiner:         seu código + pacotes Python + SO completo  →  roda em isolamento
```

---

## ✏️ Exercício 7.1 — Diagnóstico do ambiente atual

**O que o exercício pede:** Sem escrever nenhum comando Docker ainda, responder por escrito o que um `venv` **não** cobre na API Bella Tavola.

**Função do exercício:**
- Tornar explícito o problema **antes** de aprender a ferramenta que o resolve
- Reconectar com a experiência concreta do `env_ci_test` da Semana 3

### Resolução

```text
1. O que o venv NÃO cobre:
   - Versão exata do Python (3.11 vs 3.9 vs 3.12)
   - Libs do sistema (libgomp do scikit-learn, libssl)
   - O binário uvicorn como processo
   - A variável HF_TOKEN
   - A porta 8000 disponível, o arquivo .env

2. No env_ci_test, o que falhou e não falhava localmente:
   - ModuleNotFoundError (pacote global não estava no requirements.txt)
   - FileNotFoundError do .env
   - Falha ao carregar modelo sem HF_TOKEN exportado

3. Entregando só os .py + requirements.txt, a pessoa ainda precisaria de:
   Python 3.11 exato, criar o .env, saber o comando do uvicorn,
   ter as libs de sistema, e torcer pela compatibilidade do SO.
   → Docker empacota tudo isso em uma única unidade.
```

**Pontos para falar no vídeo:**
- Esse exercício é a **ponte** com a Semana 3: o `venv` revelou dependências faltando, mas ele só isola pacotes Python
- A pergunta-chave: *"o que mais precisa estar certo além do `pip install`?"* — é exatamente o vão que o contêiner preenche

---

## ✏️ Exercício 7.2 — Instalação e verificação

**O que o exercício pede:** Instalar o Docker, rodar `docker --version` e `docker run hello-world`, e ler com atenção a saída do `hello-world`.

**Função do exercício:**
- Confirmar o ambiente funcionando
- Entender, pela própria mensagem do `hello-world`, o que acontece no primeiro `run`

### Resolução

```bash
# PRIMEIRO RUN - imagem não está em cache
$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
719385e32844: Pull complete
Digest: sha256:90659bf80b44ce6555ffb2d...
Status: Downloaded newer image for hello-world:latest

Hello from Docker!
This message shows that your installation appears to be working correctly.
...

# SEGUNDO RUN - imagem está em cache (não faz pull)
$ docker run hello-world
Hello from Docker!
# ← Mais rápido, nenhuma linha "Unable to find" nem "Pulling"
```

**Checklist do que observar:**

| Conceito | O que fazer | O que NÃO fazer |
|----------|-------------|-----------------|
| **Cache de imagens** | Reutiliza imagem no 2º run | Esperar baixar tudo de novo |
| **Ciclo de vida** | Ver com `docker ps -a` que o contêiner ainda existe | Pensar que some automaticamente |
| **Limpeza** | Usar `docker run --rm hello-world` para auto-limpar | Deixar acumular centenas de contêineres mortos |

**Pontos para falar no vídeo:**
- O `hello-world` é didático de propósito: a saída **descreve o que acabou de acontecer**
- Já aqui aparece a primeira lição de ciclo de vida: contêiner parado **não desaparece sozinho** — isso volta no Bloco 8

---

# 🔵 BLOCO 8 — Primeiros comandos: rodando contêineres

## Visual: Ciclo de vida do contêiner

```
┌─────────────┐
│   IMAGEM    │  (receita, classe, arquivo estático no disco)
│ bella-tavola│
│     :v1     │  docker pull, docker build
└──────┬──────┘
       │
       │ docker run
       ↓
┌────────────────────────┐
│  CONTÊINER RODANDO     │  (bolo assado, instância, processo)
│  ID: a3f2b1c9d8e7      │
│  Status: Up 3 seconds  │
│  Porta: 8000           │
└───────────┬────────────┘
            │
    ┌───────┴────────┐
    │ docker stop    │
    │ (ou Ctrl+C)    │
    ↓                │
┌────────────────┐   │
│ CONTÊINER      │   │
│ PARADO         │   │
│ Status: Exited │   │
└────┬───────────┘   │
     │               │
     │ docker rm     │
     ↓               │
  REMOVIDO           │
                     │
 (ou com --rm,       │
  remove direto)─────┘
```

## 🧠 Conceitos-chave do Bloco 8

- **Ciclo de vida:** `pull` → imagem local → `run` → contêiner rodando → `stop` → parado → `rm` → removido. Contêineres parados **ocupam disco** e ficam em `docker ps -a`.
- **Comandos essenciais:** `run -it` (shell interativo), `run -d` (background), `run -p` (mapear porta), `run --rm` (auto-remover), `ps` / `ps -a`, `stop`, `rm`, `images`, `rmi`, `logs` / `logs -f`, `exec -it`.
- **Mapeamento de portas:** `-p PORTA_HOST:PORTA_CONTAINER`. O contêiner tem rede isolada — a porta 8000 interna **não é** automaticamente a 8000 do host.
- **Efemeridade:** cada `run` cria um contêiner **novo** a partir da imagem. Nada escrito dentro de um contêiner volta para a imagem ou aparece em outro.
- **Layers:** cada instrução do Dockerfile vira uma camada; o `pull` baixa só as camadas que faltam (`docker history` mostra as camadas).

---

## ✏️ Exercício 8.1 — Explorando o contêiner do Python

**O que o exercício pede:** Entrar num contêiner com `docker run -it python:3.11-slim bash`, explorar (`python --version`, `pip list`, `cat /etc/os-release`, `whoami`), criar `/tmp/teste.txt`, sair, entrar de novo e procurar o arquivo.

**Função do exercício:**
- Sentir na prática o isolamento e a **efemeridade** do sistema de arquivos
- Ver que o SO de dentro é Debian, independente do host

### Resolução - Passo a passo

```bash
# PRIMEIRO RUN - criar arquivo dentro do contêiner
$ docker run -it python:3.11-slim bash
root@a3f2b1c9d8e7:/# python --version
Python 3.11.9

root@a3f2b1c9d8e7:/# pip list
Package    Version
---------- -------
pip        24.0
setuptools 65.5.0
# ← Vazio! Nenhum fastapi, scikit-learn, nada.

root@a3f2b1c9d8e7:/# cat /etc/os-release | grep PRETTY_NAME
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
# ← SO é Debian, independente do seu macOS/Windows

root@a3f2b1c9d8e7:/# echo "olá do contêiner" > /tmp/teste.txt
root@a3f2b1c9d8e7:/# exit
# Você volta ao terminal do host

# SEGUNDO RUN - procurar o arquivo que criou antes
$ docker run -it python:3.11-slim bash
root@b4e3c2d1f9a8:/# cat /tmp/teste.txt
cat: /tmp/teste.txt: No such file or directory
# ← ARQUIVO DESAPARECEU! É um contêiner NOVO, não o anterior.

root@b4e3c2d1f9a8:/# exit
```

**Por que isso é importante para a Bella Tavola:**

- Cada `docker run` = novo contêiner a partir da imagem
- Dados criados dentro (banco SQLite, logs, uploads) desaparecem
- Solução: usar **volumes** (Bloco 10, Parte 2)

**Pontos para falar no vídeo:**
- O `pip list` "vazio" (sem fastapi/scikit-learn) prova que a imagem base é mínima — tudo que a API usa precisa ser instalado explicitamente
- A efemeridade não é bug, é design — e já planta a necessidade de **volumes**

---

## ✏️ Exercício 8.2 — Rodando uma API em background

**O que o exercício pede:** Rodar Nginx com `-d -p 8080:80 --name`, verificar com `docker ps`, ler `docker logs`, testar com `curl`, parar e remover. Depois repetir com `--rm` e comparar.

**Função do exercício:**
- Dominar modo detached, mapeamento de porta e leitura de logs sem entrar no contêiner
- Entender o efeito do `--rm` no ciclo `stop`/`rm`

### Resolução - Ciclo completo

```bash
# PASSO 1: Rodar em background com -d
$ docker run -d -p 8080:80 --name meu-nginx nginx
a3f2b1c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a
# ← ID longo do contêiner, terminal volta na hora (não bloqueia)

# PASSO 2: Verificar que está rodando
$ docker ps
CONTAINER ID   IMAGE     COMMAND                  STATUS         PORTS
a3f2b1c9d8e7   nginx     "/docker-entrypoint.…"   Up 3 seconds   0.0.0.0:8080->80/tcp

# PASSO 3: Ler logs
$ docker logs meu-nginx
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty...

# PASSO 4: Acompanhar em tempo real
$ docker logs -f meu-nginx
# (em outro terminal: curl http://localhost:8080)
127.0.0.1 - - [22/Jun/2026:19:45:23 +0000] "GET / HTTP/1.1" 200 ...
# ← Ctrl+C sai do follow (contêiner CONTINUA rodando)

# PASSO 5: Parar e remover
$ docker stop meu-nginx
meu-nginx

$ docker ps -a | grep meu-nginx
a3f2b1c9d8e7   nginx   ...   Exited (0)
# ← Contêiner ainda existe, mas parado

$ docker rm meu-nginx
meu-nginx

$ docker ps -a | grep meu-nginx
# ← Nada! Contêiner foi deletado
```

**Comparação: COM e SEM `--rm`**

```bash
# SEM --rm: você precisa remover manualmente
$ docker run -d -p 8080:80 --name web nginx
# ... depois ...
$ docker stop web && docker rm web  # 2 comandos

# COM --rm: remove automaticamente ao parar
$ docker run -d -p 8080:80 --rm --name web nginx
$ docker stop web
# ← Pronto, sumiu de docker ps -a
```

**Quando usar cada um:**

| Situação | Use | Motivo |
|----------|-----|--------|
| API/serviço em produção | **SEM** `--rm` | Você quer debugar se falhar |
| Script one-off / migração | COM `--rm` | Não precisa do pós-mortem |
| Teste rápido | COM `--rm` | Menos limpeza manual |

**Pontos para falar no vídeo:**
- Distinção que confunde: `docker logs -f` (follow) ≠ `docker stop`. Sair do follow não para nada.
- `--rm` é conveniência **com custo**: você perde a capacidade de inspecionar o post-mortem

---

## ✏️ Exercício 8.3 — Inspecionando um contêiner em execução

**O que o exercício pede:** Com um Nginx em background, entrar com `docker exec -it ... bash`, rodar `ps aux`, `env`, `ls /etc/nginx`, sair e confirmar que o contêiner continua de pé.

**Função do exercício:**
- Diferenciar `exec` de `run` e entender debug em produção sem derrubar o serviço

### Resolução - Diferença: `run -it` vs `exec -it`

```bash
# Cenário: Nginx rodando em background
$ docker run -d --name meu-nginx nginx
a3f2b1c9d8e7

# --- MÉTODO 1: docker run -it (novo contêiner, bash é processo principal)
$ docker run -it nginx bash
root@b4e3c2d1f9a8:/# exit
# ← Quando saiu, esse contêiner também foi removido (era só pra isso)

# --- MÉTODO 2: docker exec -it (no contêiner JÁ RODANDO)
$ docker exec -it meu-nginx bash
root@a3f2b1c9d8e7:/app# ps aux
USER   PID %CPU %MEM    COMMAND
root     1  0.0  0.0    nginx: master process
...
root    15  0.0  0.0    bash       ← você está aqui
# ↑ Pouquíssimos processos! Isolamento total.

root@a3f2b1c9d8e7:/app# exit
# ← Saiu do bash, mas meu-nginx continua rodando!

$ docker ps | grep meu-nginx
a3f2b1c9d8e7   nginx   ...   Up 2 minutes
# ← Continua de pé
```

**Caso de uso real — Debugar em produção sem derrubar:**

```bash
# Cenário: API está rodando, preciso verificar o arquivo de config
$ docker exec -it bella-api cat /app/config.json
{...}  # ← Leu o arquivo

# Scenario: API em problema, preciso rodar um comando de diagnóstico
$ docker exec -it bella-api curl http://db-service:5432
# ← Testou conectividade, API continua servindo
```

**Pontos para falar no vídeo:**
- `exec` é a ferramenta de "entrar no paciente sem desligá-lo" — essencial em produção
- O número minúsculo de processos visualiza o isolamento melhor que qualquer slide

---

## ✏️ Exercício 8.4 — Limpeza do ambiente

**O que o exercício pede:** Rodar `docker system df`, depois `docker system prune` (sem `-a`) e comparar; refletir sobre os perigos do `-a` numa máquina de CI.

**Função do exercício:**
- Manter o ambiente local saudável e entender o que cada nível de limpeza apaga

### Resolução - Diagnóstico e limpeza

```bash
# PASSO 1: Ver quanto espaço Docker está usando
$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          5         1         2.1GB     1.8GB (85%)
Containers      12        0         245MB     245MB (100%)
Local Volumes   3         0         512MB     512MB (100%)
Build Cache     47        0         3.2GB     3.2GB (100%)
# ↑ Contêineres parados = 245MB de lixo!

# PASSO 2: Limpar SEM remover imagens com tag (seguro)
$ docker system prune
WARNING! This will remove:
  - all stopped containers
  - all networks not used by at least one container
  - all dangling images
  - all build cache

Are you sure? [y/N] y
Deleted Containers: 12
Deleted Networks: 3
Deleted Build Cache: 3.2GB
Total reclaimed space: 3.5GB

# PASSO 3: Ver o resultado
$ docker system df
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          5         1         2.1GB     300MB (14%)
Containers      1         1         15MB      0B (0%)
Local Volumes   0         0         0B        0B
Build Cache     0         0         0B        0B
```

**⚠️ AVISO: `docker system prune -a` é perigoso**

```bash
# NÃO faça isso em máquina de CI!
$ docker system prune -a
# Remove também imagens sem tag (python:3.11-slim, etc)
# Próximo build tem que baixar TUDO de novo (~minutos)
# É o oposto de actions/cache@v4 da Semana 3

# ✅ Para limpeza manual segura em CI:
docker system prune  # SEM -a
# Mantém o cache de imagens base intacto
```

**Pontos para falar no vídeo:**
- Conectar com a Semana 3: cache existe justamente para **não** refazer trabalho caro
- `prune -a` é a faca de dois gumes — libera espaço, mas joga fora o cache que te economiza minutos

---

# 🔵 BLOCO 9 — Dockerfile: contêinerizando a API

## Visual: Layers e Cache de Build

```
Dockerfile                          Build Output
────────────────────────────────    ────────────────────────────────
FROM python:3.11-slim          →    Layer 1: Python 3.11 base (130MB)
WORKDIR /app                   →    Layer 2: /app directory
COPY requirements.txt .        →    Layer 3: requirements.txt
RUN pip install --no-cache...  →    Layer 4: 47 pacotes instalados
COPY . .                       →    Layer 5: código da API
EXPOSE 8000                    →    Layer 6: metadados (sem camada)
CMD ["uvicorn", ...]           →    Layer 7: metadados (sem camada)
────────────────────────────────    ────────────────────────────────

Cada instrução = 1 camada (exceto EXPOSE e CMD)
Total: ~772MB (viável para produção)

┌──────────────────────────────────────────────────┐
│ CACHE DE BUILD — Por que a ordem importa        │
├──────────────────────────────────────────────────┤
│  Alteração em:        Cache até...               │
│  ────────────────────────────────────────────    │
│  main.py         →    Layer 4 (RUN pip)    ✅   │
│                       Rebuild desde Layer 5      │
│                       Tempo: ~2 segundos         │
│                                                  │
│  requirements.txt →   Layer 3 (COPY req)   ❌   │
│                       Rebuild desde Layer 4      │
│                       Tempo: ~4 minutos          │
│                       (pip install reexecuta!)   │
│                                                  │
│  Se COPY . . fosse antes de RUN pip:            │
│  Qualquer .py   →    ZERO cache salvado   ❌❌   │
│                       Rebuild tudo               │
│                       Tempo: ~5 minutos sempre   │
└──────────────────────────────────────────────────┘
```

## 🧠 Conceitos-chave do Bloco 9

- **Anatomia:** `FROM` (imagem base) → `WORKDIR` (diretório de trabalho) → `COPY requirements.txt .` → `RUN pip install` → `COPY . .` → `EXPOSE` (só documenta) → `CMD` (comando ao iniciar).
- **`--host 0.0.0.0` é obrigatório:** o uvicorn por padrão ouve em `127.0.0.1`, que dentro do contêiner é só o próprio contêiner. `0.0.0.0` = todas as interfaces, inclusive a que liga contêiner ↔ host.
- **`CMD` em forma de lista JSON** (`["uvicorn", ...]`) evita um shell intermediário.
- **A regra de ouro do cache:** o Docker reusa camadas que não mudaram, mas **invalida tudo após a primeira mudança**. Por isso `COPY requirements.txt .` + `RUN pip install` vêm **antes** de `COPY . .` — assim mexer no código não reexecuta o `pip install`.
- **Build context:** o `.` em `docker build .` envia **todo o diretório** ao daemon (incluindo `.git`, `.env`, `venv`). O `.dockerignore` (Parte 2) resolve isso.

---

## ✏️ Exercício 9.1 — O primeiro Dockerfile

**O que o exercício pede:** Escrever o `Dockerfile` da Bella Tavola, buildar, e atravessar **dois checkpoints de falha esperada** — (A) rodar sem `-p`; (B) rodar com `-p` mas sem `--host 0.0.0.0` — antes de chegar à versão correta.

**Função do exercício:**
- Construir o artefato central da série
- Aprender os dois erros de conectividade **causando-os de propósito**

### Resolução - Dockerfile correto

```dockerfile
# Imagem base: Python 3.11 mínimo (Debian slim)
FROM python:3.11-slim

# Diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia APENAS requirements.txt primeiro (otimiza cache)
COPY requirements.txt .

# Instala dependências (--no-cache-dir reduz tamanho)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código depois (mudanças aqui não invalidam pip install)
COPY . .

# Documenta que usa porta 8000
EXPOSE 8000

# Comando padrão ao iniciar
# --host 0.0.0.0 é OBRIGATÓRIO (ver Falha B)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build inicial

```bash
$ docker build -t bella-tavola:v1 .
[1/5] FROM python:3.11-slim
[2/5] WORKDIR /app
[3/5] COPY requirements.txt .
[4/5] RUN pip install --no-cache-dir -r requirements.txt
...
[5/5] COPY . .
Successfully built e52d616058ff

$ docker images bella-tavola
REPOSITORY    TAG    IMAGE ID       SIZE
bella-tavola  v1     e52d616058ff   772MB
```

### CHECKPOINT DE FALHA A — Sem `-p`

```bash
$ docker run --rm bella-tavola:v1
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

# (em outro terminal)
$ curl http://localhost:8000/
curl: (7) Failed to connect to localhost port 8000 after 2243 ms: Could not connect to server
# ← "Connection refused" — a porta não foi mapeada!
```

**Por que falha?** A porta 8000 existe **dentro do contêiner**, mas o host não sabe como chegar lá. É como ter um servidor em um quarto sem porta.

### CHECKPOINT DE FALHA B — Com `-p` mas SEM `--host 0.0.0.0`

```dockerfile
# Versão com bug para demonstração
CMD ["uvicorn", "src.main:app", "--port", "8000"]
# ← removemos --host 0.0.0.0
```

```bash
$ docker build -t bella-tavola:sem-host .
$ docker run -p 8000:8000 --rm bella-tavola:sem-host
INFO:     Uvicorn running on http://127.0.0.1:8000

# (em outro terminal)
$ curl http://localhost:8000/
curl: (7) Failed to connect to localhost port 8000 after 2243 ms: Could not connect to server
# ← Mesma falha! Mas por motivo diferente.
```

**Por que falha?** O uvicorn ouve em `127.0.0.1` (loopback) **dentro do contêiner**. A porta `-p 8000:8000` mapeia a interface de rede do contêiner, mas o uvicorn está em outro endereço. É como ter uma porta no quarto, mas o servidor está numa sala interna sem janelas.

### Versão correta funcionando

```bash
# Restaurar o Dockerfile original com --host 0.0.0.0
$ docker build -t bella-tavola:v1 .
$ docker run -p 8000:8000 --rm bella-tavola:v1
INFO:     Uvicorn running on http://0.0.0.0:8000

# (em outro terminal)
$ curl http://localhost:8000/
{"restaurante":"Bella Tavola","versao":"1.0.0"}
# ← SUCESSO!

$ curl http://localhost:8000/health
{"status":"ok","servico":"Bella Tavola API"}
```

**Resumo: Por que ambos são necessários**

| Flag | O que faz | Sem isso... |
|------|-----------|-----------|
| `-p 8000:8000` | Mapeia a porta do host para a porta do contêiner | Porta 8000 não sai do contêiner |
| `--host 0.0.0.0` | Uvicorn ouve em TODAS as interfaces de rede | Uvicorn ouve só em 127.0.0.1 (local) |

## Visual: -p vs --host (o que cada um faz)

```
┌─────────────────────────────────────────────────────────────┐
│ FALHA A: SEM -p (porta não mapeada)                         │
├─────────────────────────────────────────────────────────────┤
│ Seu Computador (host)      Contêiner                        │
│ ─────────────────────      ────────────                     │
│ localhost:8000 ✗            0.0.0.0:8000 (uvicorn rodando)  │
│                             ↑ Não sai do contêiner          │
│                             Isolamento de rede              │
│                                                              │
│ curl http://localhost:8000                                  │
│ → Connection refused (não consegue chegar)                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FALHA B: COM -p MAS SEM --host 0.0.0.0                      │
├─────────────────────────────────────────────────────────────┤
│ Seu Computador (host)      Contêiner                        │
│ ─────────────────────      ────────────                     │
│ localhost:8000 ←─────────→ 127.0.0.1:8000 (uvicorn)        │
│ (porta mapeada!)            ↑ Loopback (só o próprio)      │
│                                                              │
│ -p 8000:8000 abre a porta, mas o uvicorn está ouvindo      │
│ em 127.0.0.1, que é só o contêiner em si.                  │
│ É como ter uma porta no quarto, mas o servidor está        │
│ numa sala interna sem janelas.                             │
│                                                              │
│ curl http://localhost:8000                                  │
│ → Connection refused / timeout                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CORRETO: COM -p E COM --host 0.0.0.0                       │
├─────────────────────────────────────────────────────────────┤
│ Seu Computador (host)      Contêiner                        │
│ ─────────────────────      ────────────                     │
│ localhost:8000 ←─────────→ 0.0.0.0:8000 (uvicorn)          │
│ (porta mapeada!)            ↑ Todas as interfaces          │
│                             ✓ Inclui a interface virtual   │
│                               que liga ao host              │
│                                                              │
│ curl http://localhost:8000                                  │
│ → {"restaurante":"Bella Tavola",...} ✅                    │
└─────────────────────────────────────────────────────────────┘
```

---

## ✏️ Exercício 9.2 — Observando o cache de build

**O que o exercício pede:** Rebuildar após alterar `main.py` (experimento 1) e após alterar `requirements.txt` (experimento 2), observando quais steps dizem `CACHED`.

**Função do exercício:**
- Ver o cache de layers na prática e sentir o impacto da ordem das instruções

### Experimento 1 — Alterar código (main.py)

```bash
# Edite src/main.py: mude alguma mensagem
$ nano src/main.py

# Rebuilde
$ docker build -t bella-tavola:v1 .
[1/5] FROM python:3.11-slim                      ← CACHED (base não mudou)
[2/5] WORKDIR /app                               ← CACHED
[3/5] COPY requirements.txt .                    ← CACHED (arquivo não mudou)
[4/5] RUN pip install --no-cache-dir ...         ← CACHED (pip install não precisa rodar)
[5/5] COPY . .                                   ← DONE (código mudou, precisa copiar)
Completed in 2.3 seconds
# ↑ Rápido! pip install foi skipped.
```

### Experimento 2 — Alterar requirements.txt

```bash
# Edite requirements.txt: adicione uma nova dependência
$ echo "requests" >> requirements.txt

# Rebuilde
$ docker build -t bella-tavola:v1 .
[1/5] FROM python:3.11-slim                      ← CACHED
[2/5] WORKDIR /app                               ← CACHED
[3/5] COPY requirements.txt .                    ← DONE (arquivo mudou)
[4/5] RUN pip install --no-cache-dir ...         ← DONE (pip install reexecutou!)
[5/5] COPY . .                                   ← DONE (tudo após 3 é refeito)
Completed in 4 minutes 23 seconds
# ↑ Lento! pip install teve que rodar.
```

**Por que a ordem importa:**

```dockerfile
# ✅ CORRETO (o que temos)
COPY requirements.txt .
RUN pip install ...
COPY . .
# Resultado: código muda → 2 segundos. Requirements muda → 4 minutos.

# ❌ ERRADO (ordem invertida)
COPY . .
RUN pip install ...
# Resultado: QUALQUER código muda → invalida pip install → 4 minutos!
# Em CI com commits frequentes, isso seria 10x mais lento.
```

**Lição de engenharia:**
- A separação dos dois `COPY` é **uma das práticas mais impactantes do Docker**
- Economiza minutos por build, especialmente em CI
- É o mesmo princípio de cache da Semana 3, aplicado a camadas de imagem

---

## ✏️ Exercício 9.3 — Nomeando e versionando imagens

**O que o exercício pede:** Buildar com duas tags (`v1` e `latest`), observar que compartilham o mesmo IMAGE ID, depois buildar `v2` **sem** atualizar `latest` e analisar para onde `latest` aponta.

**Função do exercício:**
- Entender que `latest` é só uma tag comum — não tem nada de automático

### Resolução - Tags e rastreabilidade

```bash
# Buildar com múltiplas tags
$ docker build -t bella-tavola:v1 -t bella-tavola:latest .
Successfully built e52d616058ff

# Ver as tags criadas (mesma imagem, dois nomes)
$ docker images bella-tavola
REPOSITORY      TAG      IMAGE ID       SIZE
bella-tavola    v1       e52d616058ff   772MB
bella-tavola    latest   e52d616058ff   772MB
# ↑ Mesmo IMAGE ID — são dois apelidos para a mesma imagem

# Fazer uma alteração e buildar v2 SEM atualizar latest
$ docker build -t bella-tavola:v2 .
Successfully built a1f3e7c0d2b4

$ docker images bella-tavola
REPOSITORY      TAG      IMAGE ID       SIZE
bella-tavola    v1       e52d616058ff   772MB
bella-tavola    v2       a1f3e7c0d2b4   775MB
bella-tavola    latest   e52d616058ff   772MB   ← AINDA aponta para v1!
```

**⚠️ Problema: `latest` ficou desatualizada**

```bash
# Cenário de problema em produção:
# Staging faz: docker pull bella-tavola:latest (pega v1)
# Production faz: docker pull bella-tavola:latest (também pega v1)
# # Mas o time esperava que tivesse a v2!

# Solução: ser EXPLÍCITO ao buildar
$ docker build -t bella-tavola:v2 -t bella-tavola:latest .
# Agora latest aponta para v2

$ docker images bella-tavola
REPOSITORY      TAG      IMAGE ID       SIZE
bella-tavola    v2       a1f3e7c0d2b4   775MB
bella-tavola    latest   a1f3e7c0d2b4   775MB   ← Agora está sincronizado
```

**Estratégia confiável para produção:**

```bash
# Em vez de :latest, usar o hash do commit Git
# (Parte 3 fará isso automaticamente no CI)
$ docker build -t bella-tavola:sha-abc1234 .
# Agora é imutável e rastreável: dado o SHA, você sabe exatamente qual código foi usado

# No CI, isso fica assim:
docker build -t bella-tavola:sha-${{ github.sha }} .
docker build -t bella-tavola:main .  # tag "latest" do branch
```

**Comparação:**

| Tag | Vantagem | Desvantagem |
|-----|----------|-----------|
| `:latest` | Conveniente, fácil de lembrar | Ambíguo, pode ficar desatualizada |
| `:v1`, `:v2` | Semântica, mas sem rastreabilidade | Qual v1 no commit? Quando foi buildada? |
| `:sha-abc1234` | Imutável, totalmente rastreável | Menos legível, mas perfeito para CI |

---

## ✏️ Exercício 9.4 — Desafio: por que Alpine falha para projetos de ML 🎯

**O que o exercício pede:** Criar `Dockerfile.alpine` com `FROM python:3.11-alpine`, tentar buildar, observar a falha e explicar a causa.

**Função do exercício:**
- Entender que "a imagem menor" nem sempre é a escolha certa em ML

### Resolução

```text
O build falha no pip install de scikit-learn/numpy:
  ERROR: Could not build wheels for scikit-learn
  error: command 'gcc' failed

Por quê: Alpine usa musl libc, não glibc. Os wheels pré-compilados do
PyPI são para glibc. No Alpine o pip não acha wheel compatível e tenta
compilar do fonte — exigindo gcc, headers, etc., que a imagem mínima
não tem. Resolver anula boa parte do ganho de tamanho.

Tamanhos típicos:
  python:3.11-slim   → ~130MB  (escolha padrão para ML)
  python:3.11-alpine →  ~52MB  (mas não funciona sem trabalho extra)
  python:3.11        → ~900MB  (grande demais)
```

**Pontos para falar no vídeo:**
- Lição de engenharia: otimização prematura. Alpine vale para Python puro, não para stack de ML com extensões C
- `slim` é o equilíbrio — esse é o motivo de `FROM python:3.11-slim` no Dockerfile real

---

# 🗺️ Mapa do que foi construído (Parte 1)

```
e05-p01  ──►  Dockerfile   →  A API Bella Tavola roda em um contêiner
                              local reproduzível (build + run + curl OK)
```

---

# ✅ Checklist de Competências — e05-p01

**Bloco 7 — Fundamentos**
- ✅ Explicar imagem vs. contêiner com minhas próprias palavras
- ✅ Explicar o que um contêiner isola além de um `venv`
- ✅ Docker instalado e `docker run hello-world` funcionando

**Bloco 8 — Primeiros comandos**
- ✅ Rodar, inspecionar, parar e remover contêineres
- ✅ Usar `docker logs` e `docker logs -f`
- ✅ Mapear portas com `-p` e entrar com `docker exec -it`
- ✅ Saber o que `docker system prune` faz e quando usar com cautela

**Bloco 9 — Dockerfile**
- ✅ Escrever um Dockerfile (FROM, WORKDIR, COPY, RUN, EXPOSE, CMD)
- ✅ Explicar por que `requirements.txt` é copiado antes do código (cache)
- ✅ Rodar a API em contêiner e entender por que `--host 0.0.0.0` é necessário

---

# 📊 Resumo Visual: O que fazer vs O que NÃO fazer

## Quick Reference — Comandos principais

```bash
# ✅ CORRETO — Ciclo típico
docker build -t minha-api:v1 .           # Build
docker run -p 8000:8000 minha-api:v1     # Run com porta mapeada
curl http://localhost:8000/              # Testar
docker ps                                 # Verificar que está rodando
docker logs -f <id>                      # Acompanhar logs
docker stop <id> && docker rm <id>       # Parar e remover

# ❌ COMUM — Erros evitáveis
docker run minha-api:v1                  # Sem -p → conexão recusada
docker run -p 8000:8000 minha-api:v1    # SEM --host 0.0.0.0 → conexão recusada
docker run minha-api:latest              # latest ficou velha, era v1, agora é v2?
docker system prune -a                   # Em CI → perde cache, rebuild lento
```

## Checklist de verificação pré-apresentação

```bash
# 1. Docker instalado?
$ docker --version
Docker version 29.5.3, build d1c06ef  ✅

# 2. API local funciona?
$ curl http://localhost:8000/
{"restaurante":"Bella Tavola",...}    ✅

# 3. Dockerfile existe?
$ ls Dockerfile
Dockerfile                             ✅

# 4. Build bem-sucedido?
$ docker build -t bella-tavola:v1 .
Successfully built e52d616058ff       ✅

# 5. Contêiner roda e responde?
$ docker run -p 8000:8000 bella-tavola:v1 &
$ curl http://localhost:8000/
{"restaurante":"Bella Tavola",...}    ✅
```

---

# 🎤 Conclusão para o Vídeo (Parte 1)

> "Nesta primeira parte da série Docker, peguei a API Bella Tavola — que até então 'funcionava na minha máquina' — e a coloquei dentro de um contêiner. A grande virada de chave foi entender que o **ambiente virtual isola só pacotes Python**, enquanto o **contêiner empacota o SO, as libs do sistema, os binários, as variáveis e a rede** em uma única unidade reproduzível.
>
> O Bloco 8 me deu a intuição do ciclo de vida — contêineres são efêmeros, e qualquer dado que a API cria desaparece quando o contêiner some (problema que vou resolver na Parte 2 com volumes). E o Bloco 9 foi o coração prático: escrevi o `Dockerfile`, entendi por que a **ordem das instruções** define o cache de build, e — causando os erros de propósito — aprendi que `-p` e `--host 0.0.0.0` precisam andar juntos para a API ficar acessível.
>
> Ao final, tenho a API rodando em contêiner e respondendo via `curl`. Dois problemas ficaram visíveis e abrem a Parte 2: o `/ml/predict` falha sem o `HF_TOKEN`, e os dados não persistem. É exatamente onde a série continua."
