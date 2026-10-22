from datetime import timedelta

import pytest
from django.utils import timezone
from model_bakery import baker
from rest_framework import serializers

from library.models import Loan
from library.serializers import BookSerializer, BorrowSerializer


def test_accepts_valid_title():
    result = BookSerializer().validate_title("Estudar Django")
    assert result == "Estudar Django"


def test_removes_extra_spaces():
    result = BookSerializer().validate_title("  Estudar Django  ")
    assert result == "Estudar Django"


def test_rejects_empty_title():
    with pytest.raises(serializers.ValidationError):
        BookSerializer().validate_title("")


# O mesmo teste roda uma vez para cada valor da lista.
@pytest.mark.parametrize("invalid_title", ["   ", None])
def test_rejects_invalid_titles(invalid_title):
    with pytest.raises(serializers.ValidationError) as error:
        BookSerializer().validate_title(invalid_title)

    assert error.value.detail == ["O título é obrigatório."]


# --- BorrowSerializer (usa o banco) -----------------------------------------


def make_borrow_serializer(user, book):
    return BorrowSerializer(data={}, context={"user": user, "book": book})


def test_borrow_creates_loan(member, book):
    serializer = make_borrow_serializer(member, book)

    assert serializer.is_valid()
    loan = serializer.save()

    assert loan.user == member
    assert loan.book == book
    assert loan.due_date == timezone.localdate() + timedelta(days=14)


def test_borrow_fails_without_available_copies(member, book):
    # Os 2 exemplares já estão com outras pessoas (o Bakery cria os usuários).
    baker.make(Loan, book=book, _quantity=2)

    serializer = make_borrow_serializer(member, book)

    assert not serializer.is_valid()
    assert serializer.errors["non_field_errors"] == ["Não há exemplares disponíveis."]


def test_borrow_fails_when_active_loan_limit_is_reached(member, book):
    # 3 empréstimos ativos do mesmo usuário, cada um de um livro diferente.
    baker.make(Loan, user=member, _quantity=3)

    serializer = make_borrow_serializer(member, book)

    assert not serializer.is_valid()
    assert serializer.errors["non_field_errors"] == ["Limite de 3 empréstimos ativos atingido."]
