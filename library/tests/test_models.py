import pytest
from django.contrib.auth.models import User
from django.utils import timezone
from model_bakery import baker

from library.models import Author, Book, Loan


def test_str_do_livro_e_o_titulo():
    # prepare cria o objeto só na memória (não salva), então este teste nem
    # precisa do banco de dados.
    book = baker.prepare(Book, title="Estudar Django")

    assert str(book) == "Estudar Django"


class TestExemplaresDisponiveis:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        """
        Monta o cenário com o Model Bakery. Roda antes de CADA teste desta
        classe, sempre com o banco limpo.
        """
        self.author = baker.make(Author, name="Machado de Assis")

        # _quantity cria vários de uma vez: 3 livros do mesmo autor, cada um
        # com 2 exemplares. Título e ISBN são inventados pelo Bakery.
        self.books = baker.make(
            Book,
            author=self.author,
            total_copies=2,
            _quantity=3
        )

        # 2 membros; username, e-mail e senha também são inventados.
        self.members = baker.make(User, _quantity=2)

        # O primeiro livro tem 1 empréstimo ativo e 1 já devolvido.
        self.borrowed_book = self.books[0]
        baker.make(Loan, book=self.borrowed_book, user=self.members[0])
        baker.make(
            Loan,
            book=self.borrowed_book,
            user=self.members[1],
            returned_at=timezone.now(),
        )

    def test_livros_sem_emprestimo_tem_todos_os_exemplares(self):
        for book in self.books[1:]:
            assert book.available_copies == 2

    def test_so_emprestimos_ativos_reduzem_os_exemplares(self):
        # 2 exemplares - 1 empréstimo ativo (o devolvido não conta)
        assert self.borrowed_book.available_copies == 1

    def test_livro_com_todos_os_exemplares_emprestados(self):
        baker.make(Loan, book=self.borrowed_book)

        assert self.borrowed_book.available_copies == 0
