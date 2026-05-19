import pytest

@pytest.mark.smoke
def test_contrato_get_prato(client):
    response = client.get("/pratos/1")
    assert response.status_code == 200
    prato = response.json()

    campos_obrigatorios = {"id", "nome", "categoria", "preco", "disponivel"}
    assert campos_obrigatorios.issubset(prato.keys())

    assert isinstance(prato["id"], int)
    assert isinstance(prato["nome"], str)
    assert isinstance(prato["categoria"], str)
    assert isinstance(prato["preco"], (int, float))
    assert isinstance(prato["disponivel"], bool)
    assert prato["preco"] > 0
    assert len(prato["nome"]) >= 3


@pytest.mark.smoke
def test_contrato_post_prato(client, prato_valido):
    response = client.post("/pratos", json=prato_valido)
    assert response.status_code in [200, 201]
    prato = response.json()

    assert "id" in prato
    assert isinstance(prato["id"], int)
    assert prato["nome"] == prato_valido["nome"]

    if "criado_em" in prato:
        assert isinstance(prato["criado_em"], str)
        assert len(prato["criado_em"]) > 0


@pytest.mark.smoke
def test_contrato_erro_404(client):
    response = client.get("/pratos/9999")
    assert response.status_code == 404
    corpo = response.json()

    assert "detail" in corpo or "erro" in corpo


@pytest.mark.smoke
def test_contrato_erro_422(client):
    response = client.post("/pratos", json={"nome": "X", "preco": -1})
    assert response.status_code == 422
    corpo = response.json()

    erros = corpo.get("detail") or corpo.get("detalhes")
    assert erros is not None
    assert isinstance(erros, (list, dict))
