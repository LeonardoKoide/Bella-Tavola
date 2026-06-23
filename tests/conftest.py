import pytest
from fastapi.testclient import TestClient

# Import from src package directly (main.py uses relative imports)
from src.main import app


@pytest.fixture
def client():
    """
    Cria um novo TestClient para cada função de teste.
    Não reinicializa o estado interno da aplicação.
    """
    return TestClient(app)


@pytest.fixture
def prato_valido():
    return {"nome": "Prato de Fixture", "categoria": "massa", "preco": 45.0, "disponivel": True}


@pytest.fixture
def bebida_valida():
    return {
        "nome": "Água de Fixture",
        "tipo": "agua",
        "preco": 8.0,
        "alcoolica": False,
        "volume_ml": 500,
    }
