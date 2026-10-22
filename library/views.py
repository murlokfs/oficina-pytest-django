from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Author, Book, Loan
from .permissions import IsLibrarianOrReadOnly, IsOwnerOrLibrarian, is_librarian
from .serializers import AuthorSerializer, BookSerializer, BorrowSerializer, LoanSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsLibrarianOrReadOnly]

    def perform_destroy(self, instance):
        # Os livros protegem o autor (on_delete=PROTECT). Respondemos 400 com
        # uma mensagem clara em vez de deixar estourar um erro 500.
        if instance.books.exists():
            raise ValidationError({"detail": "Não é possível excluir um autor que possui livros."})
        instance.delete()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("author")
    serializer_class = BookSerializer
    permission_classes = [IsLibrarianOrReadOnly]

    # Qualquer usuário autenticado pode pegar um livro emprestado, por isso
    # esta action troca a IsLibrarianOrReadOnly por IsAuthenticated.
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def borrow(self, request, pk=None):
        book = self.get_object()
        serializer = BorrowSerializer(data={}, context={"user": request.user, "book": book})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoanViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrLibrarian]

    def get_queryset(self):
        queryset = Loan.objects.select_related("user", "book")

        # Só a LISTAGEM é filtrada por usuário. Nas rotas de detalhe (retrieve
        # e return) buscamos entre todos os empréstimos e deixamos a
        # IsOwnerOrLibrarian decidir. Assim, acessar o empréstimo de outra
        # pessoa responde 403 (proibido) em vez de 404 (não encontrado).
        if self.action == "list" and not is_librarian(self.request.user):
            queryset = queryset.filter(user=self.request.user)

        return queryset

    # "return" é palavra reservada do Python, então o método se chama
    # return_loan, mas a URL continua sendo /loans/{id}/return/.
    @action(detail=True, methods=["post"], url_path="return", url_name="return")
    def return_loan(self, request, pk=None):
        loan = self.get_object()

        if loan.returned_at is not None:
            return Response(
                {"detail": "Este empréstimo já foi devolvido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        loan.returned_at = timezone.now()
        loan.save(update_fields=["returned_at"])
        return Response(LoanSerializer(loan).data)
