import pytest
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from library.permissions import is_librarian

# Todos os testes deste arquivo usam o banco de dados.
pytestmark = pytest.mark.django_db


def test_cadastro_cria_membro_e_retorna_token(api_client):
    data = {
        "username": "maria",
        "email": "maria@example.com",
        "password": "Senha-forte-123",
        "password_confirm": "Senha-forte-123",
    }

    response = api_client.post("/api/auth/register/", data, format="json")

    assert response.status_code == 201
    assert "password" not in response.data

    user = User.objects.get(username="maria")
    assert response.data["token"] == Token.objects.get(user=user).key
    assert not is_librarian(user)


def test_login_falha_com_senha_errada(api_client):
    User.objects.create_user(username="maria", password="Senha-forte-123")

    response = api_client.post(
        "/api/auth/login/", {"username": "maria", "password": "senha-errada"}, format="json"
    )

    assert response.status_code == 400
    assert response.data == {"detail": "Credenciais inválidas."}


def test_me_exige_autenticacao(api_client):
    response = api_client.get("/api/auth/me/")

    assert response.status_code == 401
