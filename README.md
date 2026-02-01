# Objectifs

- Suivre et enregistrer l'avancée du travail dans les vignes.
- Comparer les travaux faits et le temps passé sur chaque tâche avec les campagnes des années précédentes.


# Installation

## Frontend

### npm
Installation :
```
npm install
npm run build-frontend
```
Mise à jour des dépendances :
```
npm update --save
```

## Base de données

### PostGreSQL
- Installer PostGreSQL et ses packages dépendants :
```
apt install postgresql postgis gdal-bin libgdal-dev
```

- Créer un rôle "superuser" pour l'utilisateur courant : `sudo -u postgres createuser [ owning_user ] -s -P`

- Créer une base de données : `createdb thurjii`

- Pour avoir accès à la base : `psql -d thurjii`

### PgAdmin
- Installer pgAdmin (interface utilisateur) :
```
$ curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
$ sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
$ sudo apt install pgadmin4
```

## Backend

### Installation du serveur Django
Installer Django :
```
python -m pip install Django djangorestframework django-cors-headers django-cors-middleware djangorestframework-gis
python -m pip install 'gdal==x.y.z' ----> Pour voir la version à installer, voir la version de gdal installée : gdalinfo --version
python -m pip install pillow
python -m pip install psycopg2-binary pyproj shapely
```

### Configuration Django
- Créer un fichier `.pg_service.conf` dans le répertoire `$HOME`, et le remplir sous cette forme :
```
[thurjii_db]
host=localhost
user=USER
dbname=thurjii
port=5432
```

- Créer un fichier `.thurjii_pgpass` dans le répertoire `backend`, et le remplir sous cette forme :
```
localhost:5432:thurjii:USER:PASSWORD
```
- Changer les permissions pour ce fichier : `chmod 600 .thurjii_pgpass`

Pour exporter la structure de la base de données, clic droit sur le schéma où se trouvent les données de Thurjii, "ERD for Schema", puis clic sur le bouton SQL dans le menu du haut.

Utiliser l'addon PostGIS ? Garder de côté cette possibilité. https://postgis.net/docs/manual-2.1/using_postgis_dbmanagement.html#PostGIS_GeographyVSGeometry

### Setup admin Django
```
python manage.py createsuperuser
```

### Migrations à faire suite à modification du modèle des données
Cela concerne des modifications du fichier `backend/api/models.py` :
```
cd backend
python manage.py makemigrations api
python manage.py migrate
```

# Utilisation

- Démarrer le site frontend : `npm run start-frontend`

  -> [Site web Thurjii](http://localhost:8080)

- Démarrer le serveur backend : `npm run start-backend`

  -> [Liste des points d'accès / architecture API](http://localhost:8081/api/)
  
  -> [Site pour administration des données](http://localhost:8081/admin)

# TODO
- Rappels : ajout, affichage, cocher comme étant fait
- Réparations
- Statistiques sur bouteilles vendues, et outil pour générer des fichiers DTI+ pour la douane
https://www.douane.gouv.fr/service-en-ligne/echanges-intra-ue-de-biens-en-dti-debweb2-dti-ex-deb
https://www.youtube.com/watch?v=yDh_lG_Ir3U