from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Project, User, Contributor, Issue, Comment
from .serializers import ProjectSerializer, RegisterSerializer, UserSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProjectAuthor, IsContributor, IsAuthorOrReadOnly, IsContributorViaIssue


class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # On ne met pas IsContributor ici

    def get_queryset(self):
        user = self.request.user
        # On retourne uniquement les projets où l'utilisateur est contributeur
        projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
        return Project.objects.filter(id__in=projects_ids)

    def perform_create(self, serializer):
        # Lorsqu'on crée un projet, l'auteur est l'utilisateur connecté
        project = serializer.save(author=self.request.user)
        # On ajoute automatiquement l'utilisateur comme contributeur (rôle "Author")
        Contributor.objects.create(user=self.request.user, project=project, role="Author")


class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        print("before loading")
        serializer = RegisterSerializer(data=request.data)
        print("RegisterSerializer")
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Inscription réussie"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')

        if project_id:
            # Vérifier que le user est contributeur du projet demandé
            if Contributor.objects.filter(user=user, project_id=project_id).exists():
                return Contributor.objects.filter(project_id=project_id)
            else:
                return Contributor.objects.none()
        else:
            # Retourner les contributors des projets où le user est contributeur
            projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
            return Contributor.objects.filter(project_id__in=projects_ids)



class IssueViewSet(ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')

        if project_id:
            if Contributor.objects.filter(user=user, project_id=project_id).exists():
                return Issue.objects.filter(project_id=project_id)
            else:
                return Issue.objects.none()
        else:
            projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
            return Issue.objects.filter(project_id__in=projects_ids)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsContributorViaIssue, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        issue_id = self.request.query_params.get('issue')

        if issue_id:
            # Vérifier que le user est contributeur du projet lié à l'issue
            try:
                issue = Issue.objects.get(id=issue_id)
            except Issue.DoesNotExist:
                return Comment.objects.none()

            if Contributor.objects.filter(user=user, project=issue.project).exists():
                return Comment.objects.filter(issue=issue)
            else:
                return Comment.objects.none()
        else:
            # Si pas de paramètre → retourner les comments des issues des projets où le user est contributeur
            projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
            issues_ids = Issue.objects.filter(project_id__in=projects_ids).values_list('id', flat=True)
            return Comment.objects.filter(issue_id__in=issues_ids)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)