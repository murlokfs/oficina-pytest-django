import pytest
from rest_framework import serializers

from library.serializers import BookSerializer


def test_aceita_titulo_valido():
    result = BookSerializer().validate_title("Estudar Django")
    assert result == "Estudar Django"


def test_remove_espacos_extras():
    result = BookSerializer().validate_title("  Estudar Django  ")
    assert result == "Estudar Django"


def test_rejeita_titulo_vazio():
    with pytest.raises(serializers.ValidationError):
        BookSerializer().validate_title("")


# O mesmo teste roda uma vez para cada valor da lista.
@pytest.mark.parametrize("invalid_title", ["   ", None])
def test_rejeita_titulos_invalidos(invalid_title):
    with pytest.raises(serializers.ValidationError) as error:
        BookSerializer().validate_title(invalid_title)

    assert error.value.detail == ["O título é obrigatório."]
