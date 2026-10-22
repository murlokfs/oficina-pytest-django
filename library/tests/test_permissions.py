"""
Testa as classes de permissão isoladamente, sem passar pelas views.

O APIRequestFactory monta uma requisição "de mentira"; basta colocar nela o
usuário e chamar o método da permissão diretamente.
"""

from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIRequestFactory

from library.models import Loan
from library.permissions import IsLibrarianOrReadOnly, IsOwnerOrLibrarian

factory = APIRequestFactory()


def make_request(method, user):
    request = getattr(factory, method)("/")
    request.user = user
    return request


# --- IsLibrarianOrReadOnly: permissão por papel ------------------------------


def test_membro_pode_ler_mas_nao_pode_escrever(member):
    permission = IsLibrarianOrReadOnly()

    assert permission.has_permission(make_request("get", member), view=None)
    assert not permission.has_permission(make_request("post", member), view=None)


def test_bibliotecario_pode_escrever(librarian):
    permission = IsLibrarianOrReadOnly()

    assert permission.has_permission(make_request("post", librarian), view=None)


# --- IsOwnerOrLibrarian: permissão por objeto --------------------------------


def test_dono_acessa_o_proprio_emprestimo(member):
    loan = baker.make(Loan, user=member)

    assert IsOwnerOrLibrarian().has_object_permission(make_request("get", member), None, loan)


def test_outro_membro_nao_acessa_o_emprestimo(member):
    loan = baker.make(Loan, user=member)
    other_member = baker.make(User)

    assert not IsOwnerOrLibrarian().has_object_permission(
        make_request("get", other_member), None, loan
    )


def test_bibliotecario_acessa_qualquer_emprestimo(member, librarian):
    loan = baker.make(Loan, user=member)

    assert IsOwnerOrLibrarian().has_object_permission(make_request("get", librarian), None, loan)
