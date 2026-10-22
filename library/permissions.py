from rest_framework.permissions import SAFE_METHODS, BasePermission

LIBRARIAN_GROUP = "Librarian"


def is_librarian(user) -> bool:
    """Bibliotecário é quem está no grupo Librarian (superuser também conta)."""
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=LIBRARIAN_GROUP).exists()


class IsLibrarianOrReadOnly(BasePermission):
    """
    Permissão por PAPEL (has_permission): decide olhando só para quem faz a
    requisição e o método HTTP, sem olhar para nenhum objeto.
    """

    message = "Apenas bibliotecários podem alterar o acervo."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_librarian(request.user)


class IsOwnerOrLibrarian(BasePermission):
    """
    Permissão por OBJETO (has_object_permission): decide olhando para o
    empréstimo específico que está sendo acessado.
    """

    message = "Você só pode acessar os seus próprios empréstimos."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or is_librarian(request.user)
