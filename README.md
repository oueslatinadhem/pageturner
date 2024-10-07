# PageTurner
Application de gestion de votre bibliothèque

## Résumé des fonctionnalités:

Constitution d'une bibliothèque virtuelle  
Ajout, modification et suppression de livres

# le projet
Ce projet présente une application web full-stack. Elle est composée d'une API REST pour gérer les données et d'une interface utilisateur intuitive pour interagir avec ces données.

# Structure du projet
Le projet est organisé de la manière suivante :
- **api**: Contient le backend de l'application, notamment :
  - **config.ini**: Fichier de configuration pour l'API.
  - **server.py**: Script Python principal exécutant le serveur et gérant les requêtes API.
  - **sql**: Scripts SQL pour la création et la mise à jour de la base de données.
- **front**: Contient le frontend de l'application, développé avec HTML, CSS et JavaScript

# Installation et lancement
## Prérequis:

Python  
Un gestionnaire de base de données SQLite (si nécessaire)  
Un navigateur web  

## Lancement:

Backend:
```Bash
cd api
python server.py
```
## Utilisation
API:

GET /items: Récupère tous les éléments.  
GET /items/:id: Récupère un élément spécifique par son ID.  
POST /items: Crée un nouvel élément.  
PUT /items/:id: Met à jour un élément existant.  
DELETE /items/:id: Supprime un élément.  

### Contribuer  
Les contributions sont les bienvenues ! Pour contribuer à ce projet, veuillez suivre ces étapes :

- Forker le dépôt.
- Créer une nouvelle branche.
- Effectuer vos modifications.
- Créer une pull request.
### Licence
Ce projet est sous licence GPL-v3.

### Auteurs
Christophe Mames - Développeur principal
### Remerciements
La Manu (école des métiers du numerique) 
- campus Le Havre
- campus virtuel

