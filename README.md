# SoftDesk - API RESTful

## Description

Ce projet est une API RESTful sécurisée développée pour la société fictive SoftDesk, dans le cadre du projet 10 de la formation OpenClassrooms.

L'API permet de gérer des projets, des contributeurs, des tickets (Issues), et des commentaires, en respectant les normes RGPD, OWASP, et les bonnes pratiques de Green Code.

Les fonctionnalités sont exposées via des endpoints REST, sécurisés par authentification JWT.

## Technologies utilisées

- Python 3.12  
- Django 5.2  
- Django REST Framework  
- Django REST Framework SimpleJWT  
- SQLite3

## Installation

1. Cloner le dépôt :

```bash
git clone https://github.com/niss-tech/project_10_opc.git
````

2. Créer et activer un environnement virtuel :

```bash
python -m venv env
source env/bin/activate  # Sur Windows : env\Scripts\activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Appliquer les migrations :

```bash
python manage.py makemigrations
python manage.py migrate
```

5. Lancer le serveur de développement :

```bash
python manage.py runserver
```

L'API sera disponible à l’adresse :
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Authentification

* POST `/api/signup/` : Inscription (âge ≥ 15 ans, consentement RGPD).
* POST `/api/login/` : Authentification (JWT access + refresh).
* POST `/api/refresh/` : Renouvellement du token.

## Endpoints

### Users

* GET `/api/users/` : Liste des utilisateurs (lecture seule).

### Projects

* GET `/api/projects/` : Projets accessibles (filtrés par `get_queryset()` → l’utilisateur ne voit que ses projets).
* POST `/api/projects/` : Création d’un projet (author et contributor auto).
* PUT / PATCH / DELETE `/api/projects/{id}/` : Actions réservées à l’auteur.

### Contributors

* GET `/api/contributors/` : Liste filtrée des contributeurs.
* GET `/api/contributors/?project=X` : Contributeurs du projet X.
* POST `/api/contributors/` : Ajout par l’auteur du projet.
* DELETE `/api/contributors/{id}/` : Suppression par l’auteur du projet.

### Issues

* GET `/api/issues/` : Issues visibles (projets où l’utilisateur est contributeur).
* GET `/api/issues/?project=X` : Issues du projet X.
* POST `/api/issues/` : Création par un contributeur.
* PUT / PATCH / DELETE `/api/issues/{id}/` : Modifications réservées à l’auteur.

### Comments

* GET `/api/comments/` : Commentaires visibles (issues des projets du contributeur).
* GET `/api/comments/?issue=X` : Commentaires de l’issue X.
* POST `/api/comments/` : Création par un contributeur.
* PUT / PATCH / DELETE `/api/comments/{id}/` : Modifications réservées à l’auteur.

## Respect du cahier des charges - Approche technique

### Architecture

* `ModelViewSet` pour gérer les endpoints REST (CRUD).
* `Serializer` pour transformer les modèles en JSON et valider la logique métier.
* Permissions personnalisées héritées de `BasePermission` :

  * `IsContributor`
  * `IsProjectAuthor`
  * `IsContributorViaIssue`
  * `IsAuthorOrReadOnly`
* Pagination configurée dans `settings.py`.

### Contrôle d'accès

* Seuls les contributeurs d’un projet peuvent accéder à ses Issues et Comments.
* Seul l’auteur d’un Issue ou Comment peut le modifier / supprimer.
* Seul l’auteur du projet peut ajouter / retirer des contributeurs.

### Optimisation et Green Code

* Pagination configurée avec `'DEFAULT_PAGINATION_CLASS'` et `'PAGE_SIZE'`.
* Querysets filtrés par projet / contributeur.
* Les requêtes REST respectent les conventions RESTful.

### RGPD

* L'utilisateur renseigne son âge et son consentement RGPD à l’inscription.
* Les utilisateurs ne voient que les projets, contributors, issues et comments auxquels ils ont accès.

### Sécurité

* Authentification JWT (via `SimpleJWT`).
* Permissions fines par ressource.
* Accès sécurisé sur toutes les routes.



Réalisé par Nisrine Adamo

