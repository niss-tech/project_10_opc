from rest_framework import serializers
from .models import User, Project, Contributor, Issue, Comment
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'age', 'can_be_contacted', 'can_data_be_shared']


class ProjectSerializer(serializers.ModelSerializer):
    # On affiche le username de l'auteur en lecture seule
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'author', 'created_time']


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'role']


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'tag', 'priority', 'status',
            'project', 'author', 'assignee_user', 'created_time'
        ]

    # Validation personnalisée pour vérifier que l'assignee_user est bien un contributeur du projet
    def validate(self, data):
        # On récupère l'instance existante si c'est un PATCH / update
        instance = getattr(self, 'instance', None)

        project = data.get('project', getattr(instance, 'project', None))
        assignee_user = data.get('assignee_user', getattr(instance, 'assignee_user', None))

        # On vérifie que l'utilisateur assigné est bien contributeur du projet
        if not Contributor.objects.filter(user=assignee_user, project=project).exists():
            raise serializers.ValidationError("L'utilisateur assigné doit être un contributeur du projet.")
        
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    uuid = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ['id', 'uuid', 'description', 'author', 'issue', 'created_time']



class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'age', 'can_be_contacted', 'can_data_be_shared']

    # Validation pour vérifier que les mots de passe correspondent et que l'utilisateur a ≥ 15 ans
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        if data['age'] < 15:
            raise serializers.ValidationError("Vous devez avoir au moins 15 ans pour vous inscrire.")
        return data

    # Méthode de création de l'utilisateur (on enlève password2 qui ne sert qu'à la validation)
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
