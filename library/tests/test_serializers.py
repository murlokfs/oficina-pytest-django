import pytest
from rest_framework import serializers

from library.serializers import BookSerializer


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
