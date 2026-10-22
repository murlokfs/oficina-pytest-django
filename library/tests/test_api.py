import pytest
from django.utils import timezone
from model_bakery import baker

from library.models import Book, Loan

# Todos os testes deste arquivo usam o banco de dados.
pytestmark = pytest.mark.django_db


# --- Livros ------------------------------------------------------------------


def test_anonymous_cannot_list_books(api_client):
    response = api_client.get("/api/books/")

    assert response.status_code == 401


def test_member_lists_books_with_available_copies(member_client, book):
    response = member_client.get("/api/books/")

    assert response.status_code == 200
    assert response.data[0]["title"] == "Estudar Django"
    assert response.data[0]["available_copies"] == 2


def test_member_cannot_create_book(member_client, book):
    data = {"title": "Novo Livro", "author": book.author.id, "isbn": "9788500000028"}

    response = member_client.post("/api/books/", data, format="json")

    assert response.status_code == 403


def test_librarian_creates_book(librarian_client, book):
    data = {"title": "Novo Livro", "author": book.author.id, "isbn": "9788500000028"}

    response = librarian_client.post("/api/books/", data, format="json")

    assert response.status_code == 201
    assert Book.objects.filter(title="Novo Livro").exists()


# --- Empréstimos -------------------------------------------------------------


def test_member_borrows_book(member_client, member, book):
    response = member_client.post(f"/api/books/{book.id}/borrow/")

    assert response.status_code == 201
    assert Loan.objects.filter(user=member, book=book).exists()


def test_member_lists_only_own_loans(member_client, member):
    my_loan = baker.make(Loan, user=member)
    baker.make(Loan, _quantity=2)  # empréstimos de outras pessoas

    response = member_client.get("/api/loans/")

    assert [loan["id"] for loan in response.data] == [my_loan.id]


def test_member_cannot_see_loan_of_another_user(member_client):
    other_loan = baker.make(Loan)

    response = member_client.get(f"/api/loans/{other_loan.id}/")

    # 403 e não 404: o empréstimo existe, mas não é seu (IsOwnerOrLibrarian).
    assert response.status_code == 403


def test_owner_returns_loan_only_once(member_client, member):
    loan = baker.make(Loan, user=member)

    first = member_client.post(f"/api/loans/{loan.id}/return/")
    second = member_client.post(f"/api/loans/{loan.id}/return/")

    assert first.status_code == 200
    assert first.data["returned_at"] is not None
    assert second.status_code == 400
    assert second.data == {"detail": "Este empréstimo já foi devolvido."}
