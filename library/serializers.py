from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import LOAN_DAYS, MAX_ACTIVE_LOANS, Author, Book, Loan


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.name", read_only=True)
    available_copies = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "author_name",
            "isbn",
            "total_copies",
            "available_copies",
            "created_at",
        ]
        # Deixa o título chegar "cru" no validate_title, que cuida dos espaços
        # e devolve a nossa mensagem de erro.
        extra_kwargs = {"title": {"allow_blank": True, "trim_whitespace": False}}

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("O título é obrigatório.")
        return value.strip()


class LoanSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Loan
        fields = [
            "id",
            "user",
            "username",
            "book",
            "book_title",
            "borrowed_at",
            "due_date",
            "returned_at",
        ]
        read_only_fields = fields


class BorrowSerializer(serializers.Serializer):
    """
    Valida e cria um empréstimo.

    Não recebe campos no corpo da requisição: o usuário e o livro chegam pelo
    context, por exemplo:

        BorrowSerializer(data={}, context={"user": user, "book": book})
    """

    def validate(self, attrs):
        user = self.context["user"]
        book = self.context["book"]

        if book.available_copies <= 0:
            raise serializers.ValidationError("Não há exemplares disponíveis.")

        active_loans = user.loans.filter(returned_at__isnull=True).count()
        if active_loans >= MAX_ACTIVE_LOANS:
            raise serializers.ValidationError(
                f"Limite de {MAX_ACTIVE_LOANS} empréstimos ativos atingido."
            )

        return attrs

    def create(self, validated_data):
        return Loan.objects.create(
            user=self.context["user"],
            book=self.context["book"],
            due_date=timezone.localdate() + timedelta(days=LOAN_DAYS),
        )

    def to_representation(self, instance):
        return LoanSerializer(instance).data
