# Installation

```
npm install
npm run build-frontend
```

## Base de données MySQL

Suivre les instructions ici : https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/

MySQL démarre automatiquement après installation. Pour connaître le statut du service : `systemctl status mysql`

- Installer MySQL workbench : `snap install mysql-workbench-community`
- Lancer nysql dans un terminal : `sudo mysql`
- Ajouter l'utilisateur suivant : `CREATE USER 'thurjii'@'localhost' IDENTIFIED BY 'chardo';`
- Créer la base/schéma : `create database [nom_domaine];`
- Donner à l'utilisateur thurjii accès à la base : `GRANT ALL PRIVILEGES ON [nom_domaine].* TO 'thurjii'@'localhost';`
- Relancer mysql via l'utilisateur "thurjii" : `mysql -u thurjii -p`
- Lancer MySQL Workbench.
- Ajouter une connexion MySQL. Hostname : 127.0.0.1, port : 3306, username : thurjii, mdp : chardo.
- Si l'erreur "The name org.freedesktop.secrets was not provided by any .service files" survient, il faut installer le package gnome-keyring : `apt install gnome-keyring`, puis redémarrer l'ordinateur, et refaire les étapes précédentes.
Sélectionner le schéma "[nom_domaine]".

Exécuter les lignes suivantes pour remplir la base de données :
```
CREATE TABLE `guillot_broux`.`parcelle` (
  `id` INT NOT NULL,
  `nom` VARCHAR(45) NULL,
  PRIMARY KEY (`id`));
```

## Serveur Django

Installer Django : `python -m pip install Django`

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