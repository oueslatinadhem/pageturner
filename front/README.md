# Front Web de l'application

Ce répertoire contient les fichiers HTML, CSS et JS nécessaires. Il est à déployer en l'état dans le dossier public d'un serveur web, ou en local sur un poste client.

L'organisation des fichiers est classique  
```
.
├── assets              ressources
│   ├── scripts         les scripts
javascript
│   │   ├── api.js      cf paragraphe suivant
│   │   └── main.js     script principal
│   └── styles          les feuilles de style
│       └── global.css  styles globaux
├── index.html          page principale HTML
└── README.md           ce fichier, ne doit pas être déployé
```
## particularités
le fichier **assets/scripts/api.js** contient la constante *APIUrl* qui est l'URL et le port permettant d'accéder à l'API. Exemple :
> APIUrl = 'http://mon_domaine.fr:3000'  

/!\ Ce fichier est à modifier pendant le déploiement pour utiliser la bonne URL et le bon port de l'API déployée

