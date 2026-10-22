from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction
from rest_framework.authtoken.models import Token

from library.models import Author, Book
from library.permissions import LIBRARIAN_GROUP

DEMO_PASSWORD = "senha-demo-123"

# (título, autor, ISBN, total de exemplares)
DEMO_BOOKS = [
    ("Dom Casmurro", "Machado de Assis", "9788500000011", 3),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "9788500000028", 2),
    ("A Hora da Estrela", "Clarice Lispector", "9788500000035", 2),
    ("Laços de Família", "Clarice Lispector", "9788500000042", 1),
    ("Olhos d'Água", "Conceição Evaristo", "9788500000059", 2),
    ("Ponciá Vicêncio", "Conceição Evaristo", "9788500000066", 2),
]


class Command(BaseCommand):
    help = "Cria usuários, autores e livros de demonstração. Pode rodar quantas vezes quiser."

    @transaction.atomic
    def handle(self, *args, **options):
        librarian_group, _ = Group.objects.get_or_create(name=LIBRARIAN_GROUP)

        librarian = self.create_user("bibliotecaria")
        librarian.groups.add(librarian_group)
        member = self.create_user("aluno")

        for title, author_name, isbn, total_copies in DEMO_BOOKS:
            author, _ = Author.objects.get_or_create(name=author_name)
            # update_or_create usa o ISBN como chave: rodar de novo não duplica.
            Book.objects.update_or_create(
                isbn=isbn,
                defaults={"title": title, "author": author, "total_copies": total_copies},
            )

        self.stdout.write(self.style.SUCCESS("Dados de demonstração prontos!"))
        self.stdout.write(f"Autores: {Author.objects.count()} | Livros: {Book.objects.count()}")
        self.stdout.write(f"Senha dos dois usuários: {DEMO_PASSWORD}")
        self.stdout.write("")
        self.stdout.write("Tokens (header 'Authorization: Token <token>'):")
        for user in (librarian, member):
            token, _ = Token.objects.get_or_create(user=user)
            self.stdout.write(f"  {user.username:<14} {token.key}")

    def create_user(self, username):
        user, _ = User.objects.get_or_create(
            username=username,
            defaults={"email": f"{username}@example.com"},
        )
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user
