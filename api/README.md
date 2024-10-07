## Ce dossier contient l'ensemble des fichiers nécessaires au fonctionnement de l'API REST du projet.

- config.ini: Fichier de configuration principal contenant le chemin et le fichier de configuration de l'API et la version de l'API
- server.py: Script Python principal exécutant le serveur HTTP et gérant les requêtes API.
- sql: Dossier contenant les scripts SQL pour la création et la mise à jour de la base de données.

### ces fichiers et dossiers sont placé ici mais auront une autre place en cas de déploiement :
- config.conf: Fichier de configuration **a déployer et renommer dans /etc/nom_de_l'application.conf, l'emplacement et le nom du fichier est à préciser dans ***config.ini***** 
- database: Dossier contenant la base de données SQLite utilisée pour stocker les données de l'application.**pour le déploiememt on choisira /var/nom_de_l'application, cet emplacement dans ***config.conf*****

# détail du fichier **config.ini**
### un bloc **[DEFAULT]**
- *config_file* : chemin et nom du fichier de configuration de l'API. exemple :
> config_file = /etc/mon_api/config.conf

- *release* : version de la release de l'API. exemple:
> release = 1.0  

/!\ ce numero de release est à modifier quand une nouvelle version est prête à être déployée
# détail du fichier **config.conf**
ce fichier peut porter un autre nom, voir *config.ini*

### un bloc **[DATABASE]**
*contient les informations pour la base de données*  
- *directory* : le chemin où la base de donnée sera enregistrée. exemple :
> directory = /var/mon_appli/database
- *version* : le numero de version de la base de données. exemple :
> version = 1  

/!\ ce numero de version ne peut être modifié que par un développeur de la partie base de données de l'API car il correspond à la version du schema de la base et non à la version de l'API

### un bloc **[SERVER]**
*contient les information pour la partie serveur de l'API*
- *port* : le numero de port sur lequel écoute l'API. Exemple :
> port = 3000
