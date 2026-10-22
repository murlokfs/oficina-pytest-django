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


def test_member_can_read_but_cannot_write(member):
    permission = IsLibrarianOrReadOnly()

    assert permission.has_permission(make_request("get", member), view=None)
    assert not permission.has_permission(make_request("post", member), view=None)


def test_librarian_can_write(librarian):
    permission = IsLibrarianOrReadOnly()

    assert permission.has_permission(make_request("post", librarian), view=None)


# --- IsOwnerOrLibrarian: permissão por objeto --------------------------------


def test_owner_can_access_own_loan(member):
    loan = baker.make(Loan, user=member)

    assert IsOwnerOrLibrarian().has_object_permission(make_request("get", member), None, loan)


def test_other_member_cannot_access_loan(member):
    loan = baker.make(Loan, user=member)
    other_member = baker.make(User)

    assert not IsOwnerOrLibrarian().has_object_permission(
        make_request("get", other_member), None, loan
    )


def test_librarian_can_access_any_loan(member, librarian):
    loan = baker.make(Loan, user=member)

    assert IsOwnerOrLibrarian().has_object_permission(make_request("get", librarian), None, loan)
