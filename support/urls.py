from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, UserViewSet, ContributorViewSet, IssueViewSet, CommentViewSet
from .views import RegisterView

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'users', UserViewSet)
router.register(r'contributors', ContributorViewSet, basename='contributor')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'comments', CommentViewSet, basename='comment')



urlpatterns = [
    path('', include(router.urls)),
    path('signup/', RegisterView.as_view(), name='signup'),
]
