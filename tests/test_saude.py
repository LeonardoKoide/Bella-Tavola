import pytest

def test_pytest_funcionando():
    """Confirma que o pytest encontrou e executou este arquivo."""
    assert 1 + 1 == 2

@pytest.mark.smoke
def test_health_check(client):
    """Testa o endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
