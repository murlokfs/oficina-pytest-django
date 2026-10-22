from rest_framework.routers import DefaultRouter

from .views import AuthorViewSet, BookViewSet, LoanViewSet

router = DefaultRouter()
router.register("authors", AuthorViewSet, basename="author")
router.register("books", BookViewSet, basename="book")
router.register("loans", LoanViewSet, basename="loan")

urlpatterns = router.urls
