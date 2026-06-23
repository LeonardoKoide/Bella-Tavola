# 🐳 Exercício 13.1 - Setup Completo (Guia Passo-a-Passo)

## ℹ️ Seu Ambiente Atual
- ✅ Docker: 29.5.3
- ✅ Git User: LeonadoKoide
- ✅ Git Email: leofkoide@outlook.com
- ✅ Docker Config: Já logado (tem credenciais)

---

## PASSO 1: Criar/Confirmar Conta Docker Hub

**Status**: Você precisa fazer isso MANUALMENTE no navegador

### Se JÁ tem conta:
1. Abra: https://hub.docker.com/
2. Faça login com suas credenciais
3. Vá para Account Settings → Username
4. **Copie seu username** (você vai precisar)

### Se NÃO tem conta:
1. Abra: https://hub.docker.com/signup
2. Crie uma conta com seu email
3. Confirme o email
4. Faça login
5. **Anote seu username**

**Seu Docker Hub Username**: ___________________________
(Você vai preencher isso após criar/confirmar a conta)

---

## PASSO 2: Criar Repositório `bella-tavola` no Docker Hub

**Status**: Manual no navegador

### Instruções:
1. Faça login em https://hub.docker.com/
2. Clique em **"Create Repository"** (ou vá para https://hub.docker.com/repositories/create)
3. Preencha:
   - **Name**: `bella-tavola`
   - **Visibility**: **Public**
   - **Description**: (opcional) "API Bella Tavola - Docker image"
4. Clique em **"Create"**

**Resultado esperado:**
- URL do repositório: `https://hub.docker.com/r/SEU-USERNAME/bella-tavola`

**Seu repositório criado?** [ ] Sim  [ ] Nao

---

## PASSO 3: Gerar Token de Acesso no Docker Hub

**Status**: Manual no navegador

### ⚠️ IMPORTANTE: Use TOKEN, NÃO SENHA!

### Instruções:
1. Faça login em https://hub.docker.com/
2. Vá para **Account Settings** → **Security** (ou direto: https://hub.docker.com/settings/security)
3. Clique em **"New Access Token"**
4. Preencha:
   - **Token name**: `bella-tavola-ci`
   - **Permissions**: Marque ✓ **Read** e ✓ **Write**
5. Clique em **"Generate"**
6. **COPIE O TOKEN** - ele aparece apenas UMA VEZ

**Token copiado?** [ ] Sim  [ ] Nao

⚠️ Se não copiar agora, terá que gerar um novo token!

---

## PASSO 4: Verificar Docker Login Localmente

Execute no terminal:

```bash
docker login
```

Quando pedir:
- **Username**: Seu username do Docker Hub
- **Password**: COLE O TOKEN (não a senha da conta)

**Resultado esperado:**
```
Login Succeeded
```

✅ **Você conseguiu fazer login?** [ ] Sim  [ ] Nao

---

## PASSO 5: Configurar Secrets no GitHub

**Status**: Automatizado com gh CLI (se tiver) ou manual

### Opção A: Com GitHub CLI (recomendado)

Se tiver `gh` instalado:
```bash
# Defina as variáveis
DOCKER_USERNAME="seu-username-do-hub"
DOCKER_PASSWORD="seu-token-gerado"

# Adicione os secrets
gh secret set DOCKER_USERNAME --body "$DOCKER_USERNAME"
gh secret set DOCKER_PASSWORD --body "$DOCKER_PASSWORD"
```

### Opção B: Manual no GitHub

1. Abra seu repositório: https://github.com/LeonadoKoide/bella-tavola
2. Vá para **Settings** → **Secrets and variables** → **Actions**
3. Clique em **"New repository secret"**
4. Crie dois secrets:

**Secret 1:**
- Name: `DOCKER_USERNAME`
- Value: (seu username do Docker Hub)
- Clique em "Add secret"

**Secret 2:**
- Name: `DOCKER_PASSWORD`
- Value: (o token que você gerou)
- Clique em "Add secret"

✅ **Secrets configurados?** [ ] Sim  [ ] Nao

---

## PASSO 6: Verificar Secrets (CLI)

Execute no terminal:

```bash
gh secret list
```

Resultado esperado:
```
DOCKER_PASSWORD  Updated ...
DOCKER_USERNAME  Updated ...
HF_TOKEN         Updated ...
```

✅ **Secrets aparecem?** [ ] Sim  [ ] Nao

---

## ✅ CHECKLIST FINAL

- [ ] Conta Docker Hub criada/confirmada
- [ ] Repositório `bella-tavola` criado (público)
- [ ] Token de acesso gerado (READ & WRITE)
- [ ] `docker login` funcionou localmente
- [ ] Secret `DOCKER_USERNAME` configurado no GitHub
- [ ] Secret `DOCKER_PASSWORD` configurado no GitHub
- [ ] `gh secret list` mostra os secrets

---

## 🚨 Se algo deu errado:

| Problema | Solução |
|----------|---------|
| `denied: requested access to the resource is denied` | Token inválido ou expirado. Gere novo. |
| `name unknown: Repository not found` | Repositório não existe. Crie em Docker Hub. |
| `Login Succeeded` mas erro depois | Token revogado. Crie novo com permissões Read & Write. |
| Secrets não aparecem em `gh secret list` | Verifique se está no branch `main`. Secrets são por repositório. |

---

## 📝 Próximo Passo

Quando TODOS os checkboxes estiverem marcados, passe para:
**Exercício 13.2** - Build e Push Manual

```bash
docker build -t seu-username/bella-tavola:v1 .
docker push seu-username/bella-tavola:v1
```

