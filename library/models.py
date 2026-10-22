from django.conf import settings
from django.db import models
from django.utils import timezone

# Regras de negócio da biblioteca
LOAN_DAYS = 14  # prazo do empréstimo, em dias
MAX_ACTIVE_LOANS = 3  # empréstimos ativos por usuário


class Author(models.Model):
    name = models.CharField("nome", max_length=150)

    class Meta:
        ordering = ["name"]
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField("título", max_length=200)
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="autor",
    )
    isbn = models.CharField("ISBN", max_length=13, unique=True)
    total_copies = models.PositiveIntegerField("total de exemplares", default=1)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "livro"
        verbose_name_plural = "livros"

    def __str__(self):
        return self.title

    @property
    def available_copies(self):
        # Empréstimo ativo é o que ainda não foi devolvido.
        active_loans = self.loans.filter(returned_at__isnull=True).count()
        return self.total_copies - active_loans


class Loan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="usuário",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="livro",
    )
    borrowed_at = models.DateTimeField("emprestado em", default=timezone.now)
    due_date = models.DateField("devolver até")
    returned_at = models.DateTimeField("devolvido em", null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_at"]
        verbose_name = "empréstimo"
        verbose_name_plural = "empréstimos"

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
