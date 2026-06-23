# 🐳 Apresentação — Caderno 05-p03: Docker para MLOps (Parte 3)

## Bella Tavola 🍝 — Integrando Docker ao pipeline de CI

> **Objetivo do caderno:** Fazer a imagem refinada da Parte 2 entrar no pipeline da Semana 3. A cada merge no `main`, se os testes passarem, a imagem é publicada automaticamente no Docker Hub — completando a sequência `qualidade → integracao → docker → relatorio` e cumprindo a promessa do final de e04-p03: *"próximo passo, deploy automático."*

---

## 🎬 Roteiro de Apresentação

1. **Introdução** — onde paramos (imagem pronta, mas só local)
2. **Setup** — os pré-requisitos externos desta parte (Docker Hub, secrets)
3. **Bloco 13 — Integrando Docker ao CI**
   - Docker Hub como registry, tags por SHA e as actions oficiais
   - Build/push manual → job no `ci.yml` → verificação → pipeline à prova de erro
4. **Conclusão** — o pipeline completo e a visão da série inteira

---

## 🛠️ Setup do Ambiente e Pré-requisitos

Este é o caderno com **mais dependências externas** da série. Confirme todos os itens:

```bash
# 1. Dockerfile com multi-stage e usuário não-root existe?
$ cat Dockerfile | grep -E 'AS builder|USER appuser'
FROM python:3.11-slim AS builder
USER appuser
# ✅ Duas linhas encontradas

# 2. O .dockerignore protege o .env?
$ docker build -t bella-tavola:v3 . && \
  docker run --rm bella-tavola:v3 find /app -name '.env'
# ✅ Nenhuma saída (arquivo não existe na imagem)

# 3. O compose sobe API + PostgreSQL + Nginx?
$ docker compose up -d && sleep 5 && curl http://localhost/
{"restaurante":"Bella Tavola","versao":"1.0.0"}
# ✅ JSON da API retornou corretamente
$ docker compose down
```

**Pré-requisitos externos:**
- ✅ **Pipeline de CI da Semana 3 verde**: jobs `qualidade`, `integracao`, `relatorio` com status ✅
- ✅ **Conta no Docker Hub**: criar em [hub.docker.com/signup](https://hub.docker.com/signup) se ainda não tem
- ✅ **Repositório `bella-tavola` no Docker Hub**: será criado no Exercício 13.1

> O Bloco 13 depende de todos esses fundamentos funcionando. Resolva qualquer falha antes de começar.

---

# 🔵 BLOCO 13 — Integrando Docker ao pipeline de CI

## Visual: Pipeline Completo (Antes e Depois)

```
┌────────────────────────────────────────────────────┐
│ ANTES (e05-p02)                                    │
├────────────────────────────────────────────────────┤
│ Push para main                                     │
│      ↓                                             │
│ ┌──────────────┐                                   │
│ │  qualidade   │ → formatação + testes smoke      │
│ └──────┬───────┘                                   │
│        ↓                                           │
│ ┌──────────────┐                                   │
│ │ integracao   │ → modelo do Hub + testes integr. │
│ └──────┬───────┘                                   │
│        ↓                                           │
│ ┌──────────────┐                                   │
│ │  relatorio   │ → resumo do pipeline             │
│ └──────────────┘                                   │
│                                                    │
│ ❌ Imagem roda só localmente, não é publicada     │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│ DEPOIS (e05-p03) — Job Docker Adicionado          │
├────────────────────────────────────────────────────┤
│ Push para main                                     │
│      ↓                                             │
│ ┌──────────────┐                                   │
│ │  qualidade   │ → formatação + testes smoke      │
│ └──────┬───────┘                                   │
│        ↓                                           │
│ ┌──────────────┐                                   │
│ │ integracao   │ → modelo do Hub + testes integr. │
│ └──────┬───────┘                                   │
│        ↓                ← código + modelo validados│
│ ┌──────────────┐                                   │
│ │   docker     │ → build + push → Docker Hub ✨   │
│ │  (NOVO)      │      tag: ${{ github.sha }}      │
│ └──────┬───────┘                                   │
│        ↓                ← imagem publicada         │
│ ┌──────────────┐                                   │
│ │  relatorio   │ → resumo com URL da imagem       │
│ └──────────────┘                                   │
│                                                    │
│ ✅ Imagem publicada automaticamente no Hub        │
│ ✅ Rastreável: SHA → commit → código exato        │
│ ✅ Portátil: `docker pull usuario/bella:SHA`     │
└────────────────────────────────────────────────────┘
```

## 🧠 Conceitos-chave do Bloco 13

- **Docker Hub = registry de imagens**, análogo ao Hugging Face Hub (registry de modelos da Semana 2): `docker push usuario/repo:tag` / `docker pull ...`.
- **Tag = estratégia de versionamento.** Em produção, usar `${{ github.sha }}` como tag dá rastreabilidade total: imagem → SHA → commit → código exato.
- **Onde o job entra:** `qualidade → integracao → docker → relatorio`. O `docker` roda **só em push para main**, depende de `integracao` — se os testes falharem, a imagem **não** é publicada.
- **Actions oficiais:** `docker/setup-buildx-action@v3` (BuildKit, habilita cache), `docker/login-action@v3` (auth segura via secrets), `docker/build-push-action@v5` (build + push com cache `type=gha`).
- **Secrets:** `DOCKER_USERNAME` e `DOCKER_PASSWORD` (sempre um **token de acesso** revogável, nunca a senha).

---

## ✏️ Exercício 13.1 — Criar conta, repositório e secrets

**O que o exercício pede:** Criar conta + repositório público `bella-tavola` no Docker Hub, gerar um **token de acesso** (Read & Write) e cadastrar `DOCKER_USERNAME` e `DOCKER_PASSWORD` como secrets no GitHub.

**Função do exercício:**
- Preparar os pré-requisitos externos antes de tocar no `ci.yml`

### Resolução

```text
Por que token e não senha:
1. Escopo limitado (só Read & Write) — a senha dá acesso total à conta
2. Revogável sem trocar a senha (que afetaria todos os serviços)
3. Rastreável: múltiplos tokens nomeados por sistema
É o mesmo raciocínio do HF_TOKEN da Semana 2.

Se o token vazar: revogar IMEDIATAMENTE no Docker Hub → gerar novo →
atualizar o secret no GitHub → limpar o commit do histórico →
checar logs de acesso por atividade suspeita.
```

**Pontos para falar no vídeo:**
- Conectar com a Semana 2: token de acesso é o **padrão da indústria** para pipelines
- O plano de resposta a vazamento é tão importante quanto a prevenção

---

## ✏️ Exercício 13.2 — Build e push manual

**O que o exercício pede:** Fazer `docker login`, `docker build -t usuario/bella-tavola:v1`, `docker push`, verificar no Hub, remover localmente e fazer `docker pull` para simular "outra máquina".

**Função do exercício:**
- Entender manualmente cada etapa antes de automatizar (mesma filosofia da Semana 3)

### Resolução - Passo a passo com output real

**Passo 1: Autenticar no Docker Hub**
```bash
$ docker login
Username: seu-usuario
Password: (colar o token de acesso)
Login Succeeded
# ✅ Agora você tem permissão para fazer push
```

**Passo 2: Build com tag no formato usuario/repositorio:tag**
```bash
$ docker build -t seu-usuario/bella-tavola:v1 .
[1/7] FROM python:3.11-slim
[2/7] WORKDIR /app
[3/7] COPY requirements.txt .
[4/7] RUN pip install --no-cache-dir -r requirements.txt
[5/7] COPY . .
[6/7] RUN addgroup --system appgroup && ...
[7/7] CMD ["uvicorn", "src.main:app", ...]
Successfully built 1234567890ab
# ✅ Imagem criada com a tag seu-usuario/bella-tavola:v1
```

**Passo 3: Verificar que a tag foi criada**
```bash
$ docker images | grep bella-tavola
seu-usuario/bella-tavola   v1       1234567890ab   2 min ago   750MB
# ✅ Tag pronta para push
```

**Passo 4: Push para o Docker Hub (primeiro push — pode levar 5-10 min)**
```bash
$ docker push seu-usuario/bella-tavola:v1
The push refers to repository [docker.io/seu-usuario/bella-tavola]
aaaaaaa: Pushed                           [5/7] 2 sec
bbbbbbb: Pushed                           [4/7] 1 min 30 sec
ccccccc: Pushed                           [3/7] 3 min
ddddddd: Pushed                           [2/7] 15 sec
eeeeeee: Pushed                           [1/7] 10 sec
v1: digest: sha256:e1d6b97... size: 3248
# ✅ Todas as layers foram enviadas
```

**Passo 5: Verificar no Docker Hub**
```
🌐 Abra: https://hub.docker.com/r/seu-usuario/bella-tavola/tags
   Você deve ver a tag 'v1' com tamanho ~750MB e data do push
```

**Passo 6: Simular outra máquina — remover local e fazer pull**
```bash
$ docker rmi seu-usuario/bella-tavola:v1
Untagged: seu-usuario/bella-tavola:v1

$ docker pull seu-usuario/bella-tavola:v1
v1: Pulling from seu-usuario/bella-tavola
aaaaaaa: Pull complete  [5/7] 2 sec
bbbbbbb: Pull complete  [4/7] (reutiliza do cache local do Hub)
ccccccc: Pull complete  [3/7] (reutiliza do cache local do Hub)
ddddddd: Pull complete  [2/7]
eeeeeee: Pull complete  [1/7]
Digest: sha256:e1d6b97...
Status: Downloaded newer image for seu-usuario/bella-tavola:v1
# ✅ Imagem baixada com sucesso
```

**Passo 7: Testar a imagem publicada**
```bash
$ docker run -p 8000:8000 --rm --env-file .env seu-usuario/bella-tavola:v1
INFO:     Started server process [1]
INFO:     Application startup complete.

# Em outro terminal:
$ curl http://localhost:8000/
{"restaurante":"Bella Tavola","versao":"1.0.0"}
# ✅ API funciona corretamente
```

**Comparação: Segundo push é MUITO mais rápido**

```bash
# Altere main.py e rebuilde:
$ docker build -t seu-usuario/bella-tavola:v2 .
[...build normal...]
Successfully built 9876543210ab

# Push da v2 (com cache de layers):
$ docker push seu-usuario/bella-tavola:v2
The push refers to repository [docker.io/seu-usuario/bella-tavola]
aaaaaaa: Layer already exists    [5/7] 1 sec  ← Não enviou de novo!
bbbbbbb: Layer already exists    [4/7] 1 sec  ← Já está no Hub
ccccccc: Layer already exists    [3/7] 1 sec  ← Reutiliza
ddddddd: Layer already exists    [2/7] 1 sec  ← Cache hit
eeeeeee: Pushed                  [1/7] 2 sec  ← Só a nova layer
v2: digest: sha256:f2e7c98... size: 3251
# ⚡ Tempo total: ~10 segundos em vez de 10 minutos!
```

**Por que tão mais rápido?**
- Primeiro push: todas as 7 layers foram enviadas (~10 min)
- Segundo push: 5 layers já existem no Docker Hub, só envia a nova (COPY . .)
- Isso é o **cache de layers compartilhado** entre versões
- Uma imagem de 1.1GB pode subir em segundos porque 99% das layers já existem

**Pontos para falar no vídeo:**
- "Faça manual antes de automatizar" — se o push manual falha, o pipeline falha igual, e é mais fácil debugar na mão
- O cache de layers compartilhado entre versões é o que torna o push barato (e o CI rápido)

---

## ✏️ Exercício 13.3 — Adicionando o job `docker` ao ci.yml

**O que o exercício pede:** Inserir o job `docker` (entre `integracao` e `relatorio`) com as três actions oficiais e cache `type=gha`, e atualizar `relatorio` para `needs: docker`.

**Função do exercício:**
- Estender o pipeline existente com build + push automáticos

### Resolução

```yaml
docker:
  runs-on: ubuntu-latest
  needs: integracao
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    - uses: docker/setup-buildx-action@v3
    - uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: |
          ${{ secrets.DOCKER_USERNAME }}/bella-tavola:${{ github.sha }}
          ${{ secrets.DOCKER_USERNAME }}/bella-tavola:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

```text
O job relatorio passa de needs: integracao para needs: docker e ganha
no resumo a linha da imagem publicada:
  echo "  Imagem: ${{ secrets.DOCKER_USERNAME }}/bella-tavola:${{ github.sha }}"
```

**Pontos para falar no vídeo:**
- As actions oficiais dão de graça: BuildKit, auth segura e **cache de layers no CI** (`type=gha`) — sem cache, cada build refaz o `pip install` (5–10 min)
- A lógica de posição: só publica **depois** que `integracao` confirmou que código + modelo estão íntegros

---

## ✏️ Exercício 13.4 — Verificando a imagem publicada pelo pipeline

**O que o exercício pede:** De qualquer pasta (simulando outra máquina), fazer `docker pull usuario/bella-tavola:$SHA`, rodar e testar `/`, `/pratos` e `/ml/predict`.

**Função do exercício:**
- Fechar o ciclo: a imagem que o CI publicou funciona como a local

### Resolução

```text
A imagem do CI e a local são equivalentes porque partem do MESMO commit:
1. actions/checkout@v4 baixa exatamente o commit que foi push
2. mesmo Dockerfile, mesmo requirements.txt no repositório
(Diferenças de bytes — timestamps, ordem — são funcionalmente nulas.)

Rastreabilidade a partir do SHA:
  git show <SHA> / git checkout <SHA>
  github.com/usuario/bella-tavola/commit/<SHA>
→ imagem em produção → SHA → commit → código → autor → data
```

**Pontos para falar no vídeo:**
- O `pull` de outra pasta é a prova de que o artefato é **portátil de verdade** — não depende do seu projeto local
- A cadeia SHA → commit → código é o que torna o sistema auditável em produção

---

## ✏️ Exercício 13.5 — Desafio: pipeline à prova de erro 🏆

**O que o exercício pede:** Introduzir um erro deliberado (quebrar uma validação, um status code ou um import), dar push no `main` e confirmar que a imagem quebrada **não** chega ao Docker Hub.

**Função do exercício:**
- Confirmar que o pipeline é um **portão**: código quebrado não vira imagem publicada

### Resolução

```text
Com o erro: qualidade/integracao falha → o job docker fica skipped →
o Docker Hub NÃO recebe imagem nova → :latest segue na última válida.
Esse é o propósito do needs: integracao.

Se docker rodasse em PARALELO com integracao (race condition):
1. integracao acha o bug
2. docker já fez build+push ao mesmo tempo
3. a imagem quebrada chega ao Hub
4. integracao falha — tarde demais
5. :latest aponta para código quebrado → deploy automático usaria ela

A sequência qualidade → integracao → docker não é burocracia:
é a garantia de qualidade > velocidade de publicação.
```

**Pontos para falar no vídeo:**
- Este é o exercício que **prova o valor** de toda a série: o pipeline protege o registry
- A race condition imaginada deixa claro por que `needs:` (sequência) importa tanto

---

# 📋 Quick Reference — URLs e Secrets

**URLs essenciais desta parte:**

| O que | URL |
|------|-----|
| Criar conta Docker Hub | https://hub.docker.com/signup |
| Criar repositório | https://hub.docker.com/repositories/create |
| Gerar token de acesso | https://hub.docker.com/settings/security (Account Settings → Security) |
| Ver repositório criado | https://hub.docker.com/r/seu-usuario/bella-tavola |
| Ver tags publicadas | https://hub.docker.com/r/seu-usuario/bella-tavola/tags |
| GitHub Secrets | https://github.com/seu-usuario/bella-tavola/settings/secrets/actions |
| Aba Actions (pipeline) | https://github.com/seu-usuario/bella-tavola/actions |

**Secrets a configurar no GitHub:**

| Secret | Valor | Onde copiar |
|--------|-------|-----------|
| `DOCKER_USERNAME` | seu-usuario | Docker Hub → Account Settings → Username |
| `DOCKER_PASSWORD` | token de acesso | Docker Hub → Account Settings → Security → Access Token |

> ⚠️ **IMPORTANTE:** Use um **token de acesso**, nunca sua senha do Docker Hub no pipeline!

---

# 🗺️ Mapa Final do Sistema Construído (série e05)

```
  e05-p01  ──►  Dockerfile              API roda em contêiner local reproduzível
  e05-p02  ──►  .dockerignore           sistema multi-serviço, seguro e enxuto
                docker-compose.yml       (API + PostgreSQL + Nginx)
                nginx.conf
                Dockerfile (refat.)      multi-stage + usuário não-root
  e05-p03  ──►  ci.yml (atualizado)      imagem publicada no Docker Hub a cada merge


                    PIPELINE FINAL (push para main)
                                ↓
                       ┌─────────────┐
                       │  qualidade  │  → formatação + testes smoke
                       └──────┬──────┘
                              ↓
                       ┌─────────────┐
                       │ integracao  │  → modelo do Hub + testes de integração
                       └──────┬──────┘
                              ↓
                       ┌─────────────┐
                       │   docker    │  → build + push (tag = github.sha)
                       └──────┬──────┘       publish: docker.io/usuario:SHA
                              ↓
                       ┌─────────────┐
                       │  relatorio  │  → resumo com URL da imagem publicada
                       └─────────────┘
```

---

# 📊 Do's and Don'ts — Segurança em Pipelines

| ✅ FAZER | ❌ NÃO FAZER |
|---------|-------------|
| Usar **token de acesso** revogável | ❌ Usar a senha do Docker Hub |
| Armazenar tokens em **GitHub Secrets** | ❌ Commitar `DOCKER_PASSWORD` no código |
| Revogar token se vazar | ❌ Trocar a senha (que afeta tudo) |
| Usar `${{ github.sha }}` como tag | ❌ Usar `:latest` como única tag |
| Fazer `docker login` interativamente em dev | ❌ Salvar credenciais em `.bashrc` |
| Usar `docker/login-action@v3` no CI | ❌ Usar `docker login` com `run:` |
| Depender de testes antes de publicar (`needs:`) | ❌ Publicar antes de testar |
| Verificar publicação manualmente antes de automatizar | ❌ Automatizar sem testar |
| Revisar logs do pipeline (`Actions` → job logs) | ❌ Assumir que funcionou sem verificar |

---

# 📌 Checklist: Tudo que você precisa fazer

**1. Docker Hub (uma só vez):**
- [ ] Conta criada em https://hub.docker.com
- [ ] Repositório `bella-tavola` criado (público)
- [ ] Token de acesso gerado (permissões: Read & Write)

**2. GitHub (uma só vez):**
- [ ] Secret `DOCKER_USERNAME` configurado (Settings → Secrets)
- [ ] Secret `DOCKER_PASSWORD` configurado (o token, não a senha)

**3. Seu projeto (código):**
- [ ] Job `docker` adicionado ao `.github/workflows/ci.yml`
- [ ] Job `relatorio` atualizado para `needs: docker`
- [ ] Commit e push para `main`

**4. Verificação (manualmente, primeira vez):**
- [ ] Pipeline verde com 4 jobs na aba Actions
- [ ] Imagem publicada no Docker Hub com tag do SHA
- [ ] `docker pull usuario/bella:SHA` funciona
- [ ] `curl http://localhost:8000/` retorna JSON

---

# ✅ Checklist de Competências — e05-p03

**Bloco 13 — CI com Docker**
- ✅ Diferenciar senha de token de acesso e por que usar tokens em pipelines
- ✅ Configurar secrets no GitHub e usá-los com `${{ secrets.NOME }}`
- ✅ Fazer build e push manual e entender o cache de layers no registry
- ✅ Adicionar o job `docker` com as actions oficiais e cache `type=gha`
- ✅ Usar o `github.sha` como tag para rastreabilidade total
- ✅ Fazer pull da imagem publicada e confirmar equivalência com a local
- ✅ Provar que código quebrado nunca chega ao Docker Hub

---

# 🎤 Conclusão para o Vídeo (Parte 3 e fechamento da série)

> "Nesta parte final, a imagem da Bella Tavola — que até então vivia só na minha máquina — passou a ser publicada automaticamente. O pipeline da Semana 3 ganhou seu quarto job: a cada merge no `main`, se `qualidade` e `integracao` passam, o job `docker` faz build e push para o Docker Hub, **com o hash do commit como tag**.
>
> Antes de automatizar, fiz o **build e push manual** — mesma filosofia da Semana 3: se falha na mão, falha no pipeline, e é mais fácil debugar. Aí montei o job com as actions oficiais do Docker, que entregam BuildKit, autenticação segura por secrets e **cache de layers no CI** (`type=gha`), que evita refazer o `pip install` de scikit-learn a cada build.
>
> O desafio final foi o que provou o ponto mais importante de toda a série: como o job `docker` **depende** de `integracao`, **código quebrado nunca vira imagem publicada**. A tag `:latest` continua apontando para a última versão válida, e qualquer deploy automático fica protegido. O pipeline não é burocracia — é a garantia de que qualidade vem antes de velocidade de publicação.
>
> Olhando a série inteira: em e05-p01 a API ganhou um `Dockerfile` e passou a rodar em contêiner; em e05-p02 virou um sistema multi-serviço seguro e enxuto; e em e05-p03 entrou no CI com publicação automática e rastreável. É a base do que se espera de qualquer projeto de ML em produção: **um ambiente idêntico em todo lugar, configurado com segurança, e publicado automaticamente só quando merece confiança.**"
