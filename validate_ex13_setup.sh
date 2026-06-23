#!/bin/bash

# Script de validação para Exercício 13.1

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  VALIDACAO: Exercício 13.1 - Setup Docker Hub + GitHub Secrets ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS_COUNT=0
TOTAL_CHECKS=0

# Função para testar
check() {
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  if [ $1 -eq 0 ]; then
    echo -e "${GREEN}✓${NC} $2"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    echo -e "${RED}✗${NC} $2"
  fi
}

echo "=== 1. Docker Login ==="
docker login --username $(gh secret list 2>/dev/null | grep DOCKER_USERNAME | awk '{print $1}') --password-stdin < /dev/null 2>/dev/null
if docker ps > /dev/null 2>&1; then
  check 0 "Docker funcionando e logado"
else
  check 1 "Docker não funciona ou não está logado"
fi
echo ""

echo "=== 2. GitHub Secrets ==="
if command -v gh &> /dev/null; then
  HAS_USERNAME=$(gh secret list 2>/dev/null | grep -c "DOCKER_USERNAME")
  HAS_PASSWORD=$(gh secret list 2>/dev/null | grep -c "DOCKER_PASSWORD")

  if [ "$HAS_USERNAME" -eq 1 ]; then
    check 0 "Secret DOCKER_USERNAME existe"
  else
    check 1 "Secret DOCKER_USERNAME NÃO existe"
  fi

  if [ "$HAS_PASSWORD" -eq 1 ]; then
    check 0 "Secret DOCKER_PASSWORD existe"
  else
    check 1 "Secret DOCKER_PASSWORD NÃO existe"
  fi
else
  echo -e "${YELLOW}⚠${NC}  GitHub CLI não instalado - pulando verificação de secrets"
  echo "   Para instalar: https://cli.github.com/manual/installation"
fi
echo ""

echo "=== 3. Docker Hub Repository ==="
echo "Para verificar se o repositório exists, abra:"
echo "  https://hub.docker.com/r/$(docker ps --format '{{.Image}}' 2>/dev/null | head -1 | cut -d: -f1)"
echo ""

echo "=== 4. Dockerfile e docker-compose.yml ==="
[ -f "Dockerfile" ] && check 0 "Dockerfile existe" || check 1 "Dockerfile NÃO existe"
[ -f "docker-compose.yml" ] && check 0 "docker-compose.yml existe" || check 1 "docker-compose.yml NÃO existe"
[ -f "nginx.conf" ] && check 0 "nginx.conf existe" || check 1 "nginx.conf NÃO existe"
[ -f ".env" ] && check 0 ".env existe" || check 1 ".env NÃO existe"
echo ""

echo "=== 5. Git Status ==="
git status > /dev/null 2>&1 && check 0 "Repositório Git válido" || check 1 "Não está em um repositório Git"
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  RESULTADO: $PASS_COUNT / $TOTAL_CHECKS testes passaram         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

if [ $PASS_COUNT -eq $TOTAL_CHECKS ]; then
  echo -e "${GREEN}✓ Parabens! Ambiente pronto para Exercício 13.2${NC}"
  echo ""
  echo "Próximos passos:"
  echo "  1. Leia o guia EX_13_1_SETUP.md"
  echo "  2. Siga as instruções para criar Docker Hub account + secrets"
  echo "  3. Execute ./validate_ex13_setup.sh novamente"
  echo "  4. Quando tudo passar, execute o Exercício 13.2"
  exit 0
else
  echo -e "${RED}✗ Ainda há passos pendentes${NC}"
  echo ""
  echo "Ações necessárias:"
  echo "  1. Se Github CLI não está instalado:"
  echo "     https://cli.github.com/manual/installation"
  echo "  2. Se secrets não existem:"
  echo "     gh secret set DOCKER_USERNAME --body 'seu-username'"
  echo "     gh secret set DOCKER_PASSWORD --body 'seu-token'"
  echo "  3. Se Docker não está logado:"
  echo "     docker login"
  exit 1
fi
