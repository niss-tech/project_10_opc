from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from .models import Project, User, Contributor
from .serializers import ProjectSerializer, RegisterSerializer, UserSerializer, ContributorSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsProjectAuthor

class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    



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
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]