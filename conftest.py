"""
Fixtures compartilhadas por todos os testes do projeto.

O pytest encontra este arquivo sozinho: basta pedir a fixture pelo nome como
parâmetro do teste, por exemplo `def test_algo(member_client, book): ...`.
"""

import pytest
from django.contrib.auth.models import Group, User
from model_bakery import baker
from rest_framework.test import APIClient

from library.models import Book
from library.permissions import LIBRARIAN_GROUP


@pytest.fixture
def api_client():
    """Cliente da API sem ninguém logado (anônimo)."""
    return APIClient()


@pytest.fixture
def member(db):
    # O Model Bakery inventa username, e-mail etc. Não precisamos de nada fixo.
    return baker.make(User)


@pytest.fixture
def librarian(db):
    user = baker.make(User)
    # O grupo já existe no banco de teste porque foi criado por uma migration.
    user.groups.add(Group.objects.get(name=LIBRARIAN_GROUP))
    return user


@pytest.fixture
def member_client(member):
    client = APIClient()
    client.force_authenticate(user=member)
    return client


@pytest.fixture
def librarian_client(librarian):
    client = APIClient()
    client.force_authenticate(user=librarian)
    return client


@pytest.fixture
def book(db):
    # Só informamos o que importa para os testes. O Model Bakery preenche o
    # resto (ISBN, data de criação...) e ainda cria o Author do FK.
    return baker.make(Book, title="Estudar Django", total_copies=2)
