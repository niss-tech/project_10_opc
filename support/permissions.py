from rest_framework.permissions import BasePermission
from .models import Project

class IsProjectAuthor(BasePermission):
    """
    Autorise uniquement l'auteur du projet à modifier les contributeurs.
    Les contributeurs peuvent voir la liste (GET).
    """

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
