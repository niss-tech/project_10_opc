from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Project, User, Contributor, Issue, Comment
from .serializers import ProjectSerializer, RegisterSerializer, UserSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProjectAuthor, IsContributor, IsAuthorOrReadOnly, IsContributorViaIssue

# ViewSet pour gérer les projets
class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]  # On ne met pas IsContributor ici pour permettre la création d'un projet

    def get_queryset(self):
        user = self.request.user
        # Retourner uniquement les projets où l'utilisateur est contributeur
        projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
        return Project.objects.filter(id__in=projects_ids)

    def perform_create(self, serializer):
        # Lorsqu'on crée un projet, on définit l'auteur automatiquement
        project = serializer.save(author=self.request.user)
        # On ajoute l'utilisateur comme contributeur avec le rôle "Author"
        Contributor.objects.create(user=self.request.user, project=project, role="Author")

# Vue pour l'inscription des utilisateurs
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Inscription ouverte sans authentification

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Inscription réussie"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ViewSet en lecture seule pour la liste des utilisateurs
class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# ViewSet pour gérer les contributeurs d'un projet
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

# ViewSet pour gérer les issues (tickets)
class IssueViewSet(ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')

        if project_id:
            # Vérifier que le user est contributeur du projet demandé
            if Contributor.objects.filter(user=user, project_id=project_id).exists():
                return Issue.objects.filter(project_id=project_id)
            else:
                return Issue.objects.none()
        else:
            # Retourner les issues des projets où le user est contributeur
            projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
            return Issue.objects.filter(project_id__in=projects_ids)

    def perform_create(self, serializer):
        # Lorsqu'on crée une issue, on définit automatiquement l'auteur
        serializer.save(author=self.request.user)

# ViewSet pour gérer les commentaires
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
            # Si aucun paramètre, retourner les comments des issues des projets où le user est contributeur
            projects_ids = Contributor.objects.filter(user=user).values_list('project_id', flat=True)
            issues_ids = Issue.objects.filter(project_id__in=projects_ids).values_list('id', flat=True)
            return Comment.objects.filter(issue_id__in=issues_ids)

    def perform_create(self, serializer):
        # Lorsqu'on crée un commentaire, on définit automatiquement l'auteur
        serializer.save(author=self.request.user)
