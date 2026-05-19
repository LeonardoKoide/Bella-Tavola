import pytest


@pytest.mark.integracao
def test_criar_prato_completo(client):
    """Teste de integração: criar prato com todos os campos"""
    prato = {"nome": "Ravioli de Ricota", "categoria": "massa", "preco": 58.0, "disponivel": True}
    response = client.post("/pratos", json=prato)
    assert response.status_code == 201 or response.status_code == 200
    data = response.json()
    assert data["nome"] == "Ravioli de Ricota"
    assert data["preco"] == 58.0


@pytest.mark.integracao
def test_criar_bebida_integracao(client, bebida_valida):
    """Teste de integração: criar bebida com validação"""
    response = client.post("/bebidas", json=bebida_valida)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "id" in data
    assert "criado_em" in data


@pytest.mark.integracao
def test_listar_pratos_com_filtro(client):
    """Teste de integração: filtrar pratos por categoria"""
    response = client.get("/pratos?categoria=pizza")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all(p["categoria"] == "pizza" for p in data)


@pytest.mark.integracao
def test_fluxo_pedido_completo(client):
    """Teste de integração: criar pedido com prato existente"""
    pedido = {"prato_id": 1, "quantidade": 2, "observacao": "Sem cebola"}
    response = client.post("/pedidos", json=pedido)
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["quantidade"] == 2
    assert data["valor_total"] == 45.0 * 2


@pytest.mark.integracao
def test_pedido_prato_indisponivel(client):
    """Teste de integração: erro ao criar pedido com prato indisponível"""
    pedido = {"prato_id": 999, "quantidade": 1}
    response = client.post("/pedidos", json=pedido)
    assert response.status_code == 404


@pytest.mark.integracao
def test_listar_bebidas_filtro_alcoolica(client):
    """Teste de integração: filtrar bebidas alcoólicas"""
    response = client.get("/bebidas?alcoolica=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert all(b["alcoolica"] is True for b in data)


@pytest.mark.integracao
def test_health_check_integracao(client):
    """Teste de integração: verificar health check da API"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "servico" in data
