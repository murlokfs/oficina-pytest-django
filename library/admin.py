from django.contrib import admin

from .models import Author, Book, Loan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "isbn", "total_copies", "available_copies"]
    search_fields = ["title", "author__name", "isbn"]


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ["user", "book", "borrowed_at", "due_date", "returned_at"]
    list_filter = ["returned_at"]
