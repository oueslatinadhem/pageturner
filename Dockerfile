# Utilise l'image de base python:3.9
FROM python:3.9

# Définir le répertoire de travail à /app
WORKDIR /app

# Copier le fichier requirements.txt dans le répertoire de travail
COPY api/requirements.txt /app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste des fichiers de l'application dans /app
COPY api/ /app

# Exposer le port 8080 (ou celui que ton application utilise)
EXPOSE 8080

# Commande pour démarrer l'application
CMD ["python", "server.py"]