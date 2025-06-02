from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, UserViewSet, ContributorViewSet
from .views import RegisterView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'users', UserViewSet)
router.register(r'contributors', ContributorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signup/', RegisterView.as_view(), name='signup'),
]
