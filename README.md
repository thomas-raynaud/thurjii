# Objectifs

- Avoir une vue d'ensemble sur l'avancée du travail dans les vignes
- Pouvoir comparer l'efficacité de l'équipe sur chaque saison (nombre d'heures passées par parcelle)
- Pense-bête : noter les choses à penser, à quel endroit il faut réparer le palissage, ...

# Installation

```
npm install
npm run build-frontend
```

## Serveur Django

Installer Django :
```
python -m pip install Django
python -m pip install djangorestframework
python -m pip install django-cors-headers
python -m pip install django-cors-middleware
```

Lorsque des modifications sont faites sur le modèle des données (`backend/api/models.py`) :
```
python manage.py makemigrations api
python manage.py migrate
```

Setup admin :
```
python manage.py createsuperuser
```

# Environnement de développement

Pour démarrer le serveur : `npm run start-backend`
Pour démarrer le site : `npm run start-frontend`

# Accès aux applications :
- [App Thurjii](http://localhost:8080)
- [Site administration des données](http://localhost:8081/admin)

# TODO
- Rappels
- Planning
- BDD
- Gestion des parcelles
- Page de stats