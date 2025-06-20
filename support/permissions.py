from rest_framework.permissions import BasePermission
from .models import Project, Contributor, Issue


# Permission : IsProjectAuthor
# Autorise uniquement l'auteur du projet à modifier les contributeurs.
# Tous les contributeurs peuvent voir la liste (GET)
class IsProjectAuthor(BasePermission):
   
    def has_permission(self, request, view):
        # GET → autorisé pour tous les utilisateurs authentifiés
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user and request.user.is_authenticated

        # POST → vérifier que l'utilisateur est auteur du projet
        if request.method == 'POST':
            project_id = request.data.get('project')
            if not project_id:
                return False  # pas de projet fourni
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                return False
            return project.author == request.user

        # Autres méthodes (PUT, PATCH, DELETE) → géré par has_object_permission
        return True

    def has_object_permission(self, request, view, obj):
        # Seul l'auteur du projet peut modifier/supprimer un Contributor
        return obj.project.author == request.user

# Permission : IsContributor
# Vérifie que l'utilisateur est contributeur du projet concerné.
class IsContributor(BasePermission):

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            # On autorise si l'utilisateur est contributeur d'au moins un projet
            return Contributor.objects.filter(user=request.user).exists()

        # POST → vérifier que l'utilisateur est contributeur du projet indiqué
        if request.method == 'POST':
            project_id = request.data.get('project')
            if not project_id:
                return False
            return Contributor.objects.filter(user=request.user, project_id=project_id).exists()

        return True


    def has_object_permission(self, request, view, obj):
        # L'utilisateur doit être contributeur du projet lié à l'objet
        return Contributor.objects.filter(user=request.user, project=obj.project).exists()
    

# Permission : IsAuthorOrReadOnly
# Seul l'auteur de l'objet peut le modifier ou le supprimer.
# Les autres utilisateurs peuvent le lire.
class IsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.author == request.user


# Permission : IsContributorViaIssue
# Vérifie que l'utilisateur est contributeur du projet de l'issue liée au commentaire.
class IsContributorViaIssue(BasePermission):

    def has_permission(self, request, view):
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return True

        if request.method in ('POST', 'GET', 'HEAD', 'OPTIONS'):
            # On récupère l'ID de l'issue dans les paramètres ou dans le corps de la requête
            issue_id = request.data.get('issue') or request.query_params.get('issue')

            if issue_id:
                try:
                    issue = Issue.objects.get(id=issue_id)
                except Issue.DoesNotExist:
                    return False
                # On vérifie que l'utilisateur est contributeur du projet de l'issue
                return Contributor.objects.filter(user=request.user, project=issue.project).exists()
            else:
                # Si pas d'issue précisée (GET /comments/) → vérifier que le user est contributeur d'au moins un projet
                return Contributor.objects.filter(user=request.user).exists()

        return True


    def has_object_permission(self, request, view, obj):
        # obj = Comment → on regarde l'issue liée → le projet de l'issue
        return Contributor.objects.filter(user=request.user, project=obj.issue.project).exists()
