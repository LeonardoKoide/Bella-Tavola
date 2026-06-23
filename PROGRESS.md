# 📊 PROGRESSO - SERIE DOCKER BELLA TAVOLA

## ✅ Completed (Completo)

### Parte 1 (e05-p01) - Dockerfile
- [x] Dockerfile criado e testado
- [x] Build funciona (772MB, cache ativo)
- [x] API responde corretamente via `docker run -p 8000:8000`
- [x] Todos os endpoints validados (/, /health)
- [x] Apresentação criada com exemplos de terminal

### Parte 2 (e05-p02) - Docker Compose + Volumes + Segurança
- [x] docker-compose.yml criado (API + PostgreSQL + Nginx)
- [x] nginx.conf criado (proxy reverso)
- [x] .dockerignore criado (remove .env e lixo)
- [x] Dockerfile refatorado com multi-stage + usuário não-root
- [x] Volumes funcionando (bella-dados, bella-pg-data)
- [x] Healthcheck do PostgreSQL configurado
- [x] Todos os 3 serviços sobem e communicam corretamente
- [x] Apresentação criada com exemplos de terminal

### Verificação e Testes
- [x] P01 - Build e endpoints testados
- [x] P02 - Docker Compose testado com sucesso
- [x] Arquivos faltantes criados durante teste

### Apresentações
- [x] apresentacao_caderno_docker_p01.md - Completa com diagramas
- [x] apresentacao_caderno_docker_p02.md - Completa com diagramas
- [x] apresentacao_caderno_docker_p03.md - Completa com URLs e checklists

---

## 🔄 In Progress (Em andamento)

### Parte 3 (e05-p03) - CI/CD com Docker Hub
- [ ] Exercício 13.1 - Setup Docker Hub + Secrets
  - [ ] Conta Docker Hub criada/confirmada
  - [ ] Repositório `bella-tavola` criado
  - [ ] Token de acesso gerado
  - [ ] Secrets `DOCKER_USERNAME` e `DOCKER_PASSWORD` configurados
  - **STATUS**: Guias criados, esperando ação manual do usuário

- [ ] Exercício 13.2 - Build e Push Manual (próximo)
- [ ] Exercício 13.3 - Job `docker` no ci.yml (próximo)
- [ ] Exercício 13.4 - Verificação de imagem publicada
- [ ] Exercício 13.5 - Pipeline à prova de erro

---

## 📁 Arquivos Criados para Suporte

### Documentação do Ex 13.1
1. **EX_13_1_SETUP.md**
   - Guia passo-a-passo detalhado (6 páginas)
   - Instruções manuais para cada etapa
   - Checklists para confirmar cada passo
   - Troubleshooting section

2. **EX_13_1_URLS.txt**
   - Resumo rápido com URLs
   - Checklist compacto
   - Bom para referência rápida

3. **validate_ex13_setup.sh**
   - Script bash para validar setup
   - Verifica Docker login
   - Verifica GitHub secrets
   - Verifica arquivos necessários

### Arquivos do Projeto
- ✅ `Dockerfile` (multi-stage + não-root)
- ✅ `docker-compose.yml` (API + DB + Nginx)
- ✅ `nginx.conf` (proxy reverso)
- ✅ `.dockerignore` (segurança + limpeza)
- ✅ `requirements.txt` (dependências)
- ✅ `.env` (variáveis de ambiente)
- ✅ `.github/workflows/ci.yml` (jobs: qualidade, integracao)
- ⏳ `.github/workflows/ci.yml` - PENDENTE: adicionar jobs docker + relatorio

---

## 📋 Resumo de Comando para Referência Rápida

### P01 - Dockerfile
```bash
docker build -t bella-tavola:v1 .
docker run -p 8000:8000 --rm bella-tavola:v1
curl http://localhost:8000/
```

### P02 - Docker Compose
```bash
docker compose up -d
docker compose ps
curl http://localhost:8000/
docker compose down
```

### P03 - CI/CD (próximo)
```bash
# Após configurar secrets:
docker login
docker build -t usuario/bella-tavola:v1 .
docker push usuario/bella-tavola:v1

# Verificar no Hub:
docker pull usuario/bella-tavola:v1
docker run -p 8000:8000 --rm --env-file .env usuario/bella-tavola:v1
```

---

## 🎯 Próximas Ações (TODO)

### HOJE - Exercício 13.1 (Manual)
1. [ ] Abra `EX_13_1_SETUP.md`
2. [ ] Siga os 6 passos (Docker Hub + GitHub Secrets)
3. [ ] Execute `bash validate_ex13_setup.sh` para verificar
4. **Tempo estimado**: 20-25 minutos

### DEPOIS - Exercício 13.2 (Build & Push)
1. [ ] `docker login` com seu username/token
2. [ ] `docker build -t seu-username/bella-tavola:v1 .`
3. [ ] `docker push seu-username/bella-tavola:v1`
4. [ ] Verificar em: `https://hub.docker.com/r/seu-username/bella-tavola/tags`
5. [ ] `docker pull seu-username/bella-tavola:v1` (simular outra máquina)
6. [ ] `docker run -p 8000:8000 --rm --env-file .env seu-username/bella-tavola:v1`

### DEPOIS - Exercício 13.3 (CI/CD Job)
1. [ ] Adicionar job `docker` ao `.github/workflows/ci.yml`
2. [ ] Atualizar job `relatorio` para `needs: docker`
3. [ ] Fazer commit e push
4. [ ] Observar pipeline na aba Actions

### DEPOIS - Exercício 13.4 (Verificação)
1. [ ] Pull da imagem publicada pelo CI
2. [ ] Rodar localmente
3. [ ] Testar endpoints

### DEPOIS - Exercício 13.5 (Desafio)
1. [ ] Introduzir erro deliberado
2. [ ] Verificar que job docker fica skipped
3. [ ] Verificar que nenhuma imagem é publicada
4. [ ] Corrigir erro e confirmar pipeline verde

---

## 🎓 Competências Adquiridas

### Após P01:
- ✓ Entender Docker basics (imagem vs contêiner)
- ✓ Escrever Dockerfile com multi-stage
- ✓ Usar docker build e docker run
- ✓ Entender cache de layers

### Após P02:
- ✓ Usar Docker Compose para orquestração
- ✓ Persistir dados com volumes
- ✓ Comunicação entre serviços
- ✓ Proxy reverso com Nginx
- ✓ Segurança: .dockerignore + não-root

### Após P03:
- ✓ Integrar Docker ao pipeline CI/CD
- ✓ Publicar imagens no Docker Hub
- ✓ Usar GitHub Secrets
- ✓ Rastreabilidade: tag = SHA do commit
- ✓ Quality gates: código quebrado ≠ imagem publicada

---

## 💡 Notas Importantes

### Segurança
- ⚠️ NUNCA commit .env no Git
- ⚠️ NUNCA use senha do Docker Hub no pipeline
- ⚠️ SEMPRE use token de acesso (revogável)
- ⚠️ Revogue token se vazar: https://hub.docker.com/settings/security

### Performance
- O cache de layers economiza tempo:
  - 1º build: ~1-2 min
  - 2º build (mesmo reqs): ~10 sec
  - Push após:  ~10 min (1x) → ~10 sec (2x)

### Debugging
- `docker logs -f CONTAINER_ID` → logs em tempo real
- `docker exec -it CONTAINER_ID bash` → shell dentro do container
- `docker compose logs -f SERVICE` → logs via compose

---

## 📞 Contato com Problemas

Se algo falhar:

1. **Docker login falha**: Token inválido ou expirado
   → Gere novo em: https://hub.docker.com/settings/security

2. **Repositório não encontrado**: Repo não existe no Hub
   → Crie em: https://hub.docker.com/repositories/create

3. **Secrets não funcionam no CI**: Usar nome correto
   → Verifique: `gh secret list`

4. **API não responde no container**: Porta não mapeada corretamente
   → Verifique: `docker run -p 8000:8000` (host:container)

---

## 📈 Estimativa Final

| Parte | Status | Tempo |
|-------|--------|-------|
| P01   | ✅ Completo | ~2h (incluindo apresentação) |
| P02   | ✅ Completo | ~3h (Compose + volumes + segurança) |
| P03   | 🔄 Em andamento | ~2h (CI/CD setup) |
| **Total** | | **~7h** |

**Próximo checkpoint**: Após completar Exercício 13.1 setup

---

**Última atualização**: 2026-06-23
**Status**: Pronto para Exercício 13.1 (manual via Docker Hub + GitHub)
