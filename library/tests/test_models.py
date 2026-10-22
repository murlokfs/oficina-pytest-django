"""
Model Bakery em ação:

    baker.prepare(Book)                -> cria só na memória (não salva, nem usa o banco)
    baker.make(Book)                   -> cria e salva, preenchendo sozinho os campos obrigatórios
    baker.make(Book, title="...")      -> fixa só os campos que importam para o teste
    baker.make(Loan, _quantity=3)      -> cria vários de uma vez

Em todos os casos, os FKs obrigatórios (Author do Book, User e Book do Loan)
são criados automaticamente.
"""

from django.utils import timezone
from model_bakery import baker

from library.models import Book, Loan


def test_book_str():
    # prepare não salva nada, então este teste nem precisa do banco.
    book = baker.prepare(Book, title="Estudar Django")

    assert str(book) == "Estudar Django"


def test_new_book_has_all_copies_available(book):
    assert book.available_copies == 2


def test_only_active_loans_reduce_available_copies(book):
    baker.make(Loan, book=book)  # ativo: returned_at fica vazio
    baker.make(Loan, book=book, returned_at=timezone.now())  # já devolvido

    assert book.available_copies == 1
