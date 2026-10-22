import pytest
from django.utils import timezone
from model_bakery import baker

from library.models import Book, Loan

# Todos os testes deste arquivo usam o banco de dados.
pytestmark = pytest.mark.django_db


# --- Livros ------------------------------------------------------------------


def test_anonimo_nao_lista_livros(api_client):
    response = api_client.get("/api/books/")

    assert response.status_code == 401


def test_membro_lista_livros_com_exemplares_disponiveis(member_client, book):
    response = member_client.get("/api/books/")

    assert response.status_code == 200
    assert response.data[0]["title"] == "Estudar Django"
    assert response.data[0]["available_copies"] == 2


def test_membro_nao_pode_criar_livro(member_client, book):
    data = {"title": "Novo Livro", "author": book.author.id, "isbn": "9788500000028"}

    response = member_client.post("/api/books/", data, format="json")

    assert response.status_code == 403


def test_bibliotecario_cria_livro(librarian_client, book):
    data = {"title": "Novo Livro", "author": book.author.id, "isbn": "9788500000028"}

    response = librarian_client.post("/api/books/", data, format="json")

    assert response.status_code == 201
    assert Book.objects.filter(title="Novo Livro").exists()


# --- Empréstimos -------------------------------------------------------------


def test_membro_pega_livro_emprestado(member_client, member, book):
    response = member_client.post(f"/api/books/{book.id}/borrow/")

    assert response.status_code == 201
    assert Loan.objects.filter(user=member, book=book).exists()


def test_membro_lista_so_os_proprios_emprestimos(member_client, member):
    my_loan = baker.make(Loan, user=member)
    baker.make(Loan, _quantity=2)  # empréstimos de outras pessoas

    response = member_client.get("/api/loans/")

    assert [loan["id"] for loan in response.data] == [my_loan.id]


def test_membro_nao_ve_emprestimo_de_outra_pessoa(member_client):
    other_loan = baker.make(Loan)

    response = member_client.get(f"/api/loans/{other_loan.id}/")

    # 403 e não 404: o empréstimo existe, mas não é seu (IsOwnerOrLibrarian).
    assert response.status_code == 403


def test_dono_devolve_o_emprestimo_uma_unica_vez(member_client, member):
    loan = baker.make(Loan, user=member)

    first = member_client.post(f"/api/loans/{loan.id}/return/")
    second = member_client.post(f"/api/loans/{loan.id}/return/")

    assert first.status_code == 200
    assert first.data["returned_at"] is not None
    assert second.status_code == 400
    assert second.data == {"detail": "Este empréstimo já foi devolvido."}
