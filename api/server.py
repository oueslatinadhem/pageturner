import sys
import os
import sqlite3
import configparser
import json
import socketserver
from http.server import BaseHTTPRequestHandler
import signal

# gestion des signaux
def signal_handler(sig, frame):
    print(' ')
    signaux = {
    signal.SIGINT: {"sig": "SIGINT", "desc": "Interruption (Ctrl+C)"},
    signal.SIGTERM: {"sig": "SIGTERM", "desc": "Demande de terminaison"},
    }
    print(f"Signal reçu : {signaux[sig]['sig']}({sig}) {signaux[sig]['desc']} ")
    print('Arrêt en cours ...')
    sys.exit(0)


# partie base de données et initialisation

def read_config():
    """Lit la configuration depuis le fichier config.ini.

    Returns:
        dict : Un dictionnaire contenant les paramètres de configuration.
    """
    ret={}
    print("chargement de la configuration")
    config = configparser.ConfigParser()
    config.read("config.ini")
    print(f'version {config["DEFAULT"]["release"]}')
    configfile=os.path.normpath(os.path.join(os.path.dirname(__file__),config['DEFAULT']['config_file']))
    config.read(configfile)
    ret['database']=os.path.normpath(os.path.join(os.path.dirname(__file__),config['DATABASE']['directory'],'database.db'))
    ret['bddver']=int(config['DATABASE']['version'])
    ret['server_port']=int(config['SERVER']['port'])
    return ret

def read_version(database):
    """Lit la version actuelle du schéma de la base de données.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.

    Returns:
        int : La version actuelle du schéma de la base de données, ou None en cas d'erreur.
    """
    result=False
    # On extrait le nom du fichier pour ne garder que le chemin du répertoire
    directory = os.path.dirname(database)
    # On vérifie si le répertoire existe déjà
    if not os.path.exists(directory):
        # Si le répertoire n'existe pas, on le crée
        os.makedirs(directory)
        print("création du dossier de la base de données")
    try:
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute("SELECT ver FROM version;")
        result = cur.fetchone()
    except sqlite3.Error as error:
        print(error)
        try:
            cur.execute("DROP TABLE version;")
            conn.commit()
        except sqlite3.Error as errdrop:
            pass
        finally:
            # creation
            print("creation de la base de données")
            try:
                cur.executescript("CREATE TABLE version ( ver INTEGER ); INSERT INTO version (ver) VALUES (0);")
                conn.commit()
            except sqlite3.Error as errcreate:
                print(errcreate)
                print('abandon')
                sys.Exit(1)
            finally:
                print(f"base créée")
                if cur:
                    cur.close()
                if conn:
                    conn.close()
                return read_version(database)
    finally:
        if result:
            version = result[0]
            return version
        if conn:
            conn.close()

def updatebdd(config,ver):
    """Met à jour le schéma de la base de données à la version spécifiée.

    Args:
        config (dict) : Le dictionnaire de configuration.
        ver (int) : La version cible.
    """
    database=config['database']
    bddver=config['bddver']
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    while ver<bddver:
        try:
            updatefile=os.path.join(os.path.dirname(__file__),f"sql/{ver}.sql")
            with open(updatefile, 'r') as f:
                requetes = f.read()
                cur.executescript(requetes)
            cur.execute("UPDATE version SET ver = ?", (ver + 1,))
            conn.commit()
            ver+=1
            print(f"database schema upgraded to v{ver}")
        except sqlite3.Error as error:
            print(error)
            sys.Exit(2)
    if cur:
        cur.close()
    if conn:
        conn.close()

# partie serveur API

def getAll(database):
    """Récupère tous les éléments de la table 'data' et les renvoie sous forme de JSON.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.

    Returns:
        list: Une liste de dictionnaires, chaque dictionnaire représentant un élément.
        None: En cas d'erreur de connexion à la base de données.
    """
    try:
        # Connexion à la base de données (à adapter à votre configuration)
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Requête SQL pour récupérer les données
        cur.execute("SELECT id, titre FROM data")
        rows = cur.fetchall()
        # Conversion des résultats en JSON
        data = []
        for row in rows:
            data.append({'id': row[0], 'titre': row[1]})
        return json.dumps(data)
    except sqlite3.Error as error:
        print(f"Une erreur s'est produite lors de l'accès à la base de données : {error}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def getOne(database,id):
    """Récupère un élément spécifique de la table 'data' en fonction de son ID.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.
        id (int): L'ID de l'élément à récupérer.

    Returns:
        dict: Un dictionnaire contenant les informations de l'élément, ou None si l'élément n'est pas trouvé.
    """
    try:
        # Connexion à la base de données (à adapter à votre configuration)
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Requête SQL pour récupérer les données
        cur.execute("SELECT id, titre, detail FROM data WHERE id=?", (id,))
        row = cur.fetchone()
        if row:
            data = {'id': row[0], 'titre': row[1], 'detail': row[2]}
            return json.dumps(data)
        else:
            return None
    except sqlite3.Error as error:
        print(f"Une erreur s'est produite lors de l'accès à la base de données : {error}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def create(database,data):
    """Crée un nouvel élément dans la table 'data' à partir des données JSON fournies.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.
        data (dict): Un dictionnaire JSON contenant les valeurs pour les champs 'titre' et 'detail'.

    Returns:
        int: L'ID de l'élément nouvellement créé, ou None en cas d'erreur.
    """
    try:
        # Connexion à la base de données (à adapter à votre configuration)
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Requête SQL pour insérer un nouvel élément
        cur.execute("INSERT INTO data (titre, detail) VALUES (?, ?)", (data['titre'], data['detail']))
        conn.commit()
        # Récupérer l'ID de l'élément inséré
        return True
    except sqlite3.Error as error:
        print(f"Une erreur s'est produite lors de la création de l'élément : {error}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update(database,data):
    """Met à jour un élément dans la table 'data' à partir des données JSON fournies.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.
        data (dict): Un dictionnaire JSON contenant les nouvelles valeurs pour l'élément à mettre à jour.

    Returns:
        bool: True si la mise à jour a réussi, False sinon.
    """
    try:
        # Connexion à la base de données (à adapter à votre configuration)
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Requête SQL pour mettre à jour l'élément
        cur.execute("UPDATE data SET titre=?, detail=? WHERE id=?", (data['titre'], data['detail'], data['id']))
        conn.commit()
        # Vérifier si au moins une ligne a été affectée
        rows_affected = cur.rowcount
        return rows_affected == 1
    except sqlite3.Error as error:
        print(f"Une erreur s'est produite lors de la mise à jour de l'élément : {error}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def delete(database,id):
    """Supprime un élément spécifique de la table 'data' en fonction de son ID.

    Args:
        database (str) : Le chemin vers le fichier de la base de données.
        id (int): L'ID de l'élément à supprimer.

    Returns:
        bool: True si la suppression a réussi, False sinon.
    """
    try:
        # Connexion à la base de données (à adapter à votre configuration)
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        # Requête SQL pour supprimer l'élément
        cur.execute("DELETE FROM data WHERE id=?", (id,))
        conn.commit()
        # Vérifier si au moins une ligne a été affectée
        rows_affected = cur.rowcount
        return rows_affected == 1
    except sqlite3.Error as error:
        print(f"Une erreur s'est produite lors de la suppression de l'élément : {error}")
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

class MyRequestHandler(BaseHTTPRequestHandler):
    """Gère les requêtes HTTP pour l'API REST.

    Cette classe hérite de la classe `BaseHTTPRequestHandler` pour implémenter des méthodes personnalisées 
    afin de gérer les requêtes HTTP pour votre API REST. Elle accède à la base de données fournie 
    dans le constructeur pour effectuer des opérations CRUD (Création, Lecture, Mise à jour, Suppression) 
    sur les données.

    Attributs:
        database (str): Le chemin d'accès à la base de données SQLite.

    Méthodes:
        do_OPTIONS(self):
            Gère les requêtes HTTP OPTIONS. Envoie les en-têtes CORS pour autoriser les requêtes cross-origin.
        do_GET(self):
            Gère les requêtes HTTP GET. Récupère des éléments de la base de données en fonction de l'URL.
            - Si le chemin est '/', renvoie tous les éléments.
            - Sinon, extrait l'ID de l'URL et récupère l'élément spécifique.
            En cas d'erreur (mauvais format d'ID ou élément introuvable), renvoie un code d'erreur 404 (NotFound).
        do_POST(self):
            Gère les requêtes HTTP POST. Crée un nouvel élément dans la base de données à partir des données JSON fournies dans le corps de la requête.
            Envoie un code d'erreur 404 (NotFound) en cas d'échec de la création.
        do_PUT(self):
            Gère les requêtes HTTP PUT. Met à jour un élément existant dans la base de données à partir des données JSON fournies dans le corps de la requête.
            Extrait l'ID de l'élément à mettre à jour à partir de l'URL.
            Envoie un code d'erreur 404 (NotFound) en cas d'échec de la mise à jour ou si l'ID n'est pas fourni.
        do_DELETE(self):
            Gère les requêtes HTTP DELETE. Supprime un élément spécifique de la base de données en fonction de l'ID fourni dans l'URL.
            Envoie un code d'erreur 404 (NotFound) en cas d'échec de la suppression ou si l'ID n'est pas fourni.
    """
    def __init__(self, request, client_address, server, database):
        """Initialise le gestionnaire de requêtes.

        Args:
            request: La requête HTTP du client.
            client_address: L'adresse du client.
            server: Le serveur HTTP.
            database (str): Le chemin d'accès à la base de données SQLite.

        **Note:** L'attribut `database` est accessible en lecture seule depuis le constructeur car les méthodes statiques ne peuvent pas modifier l'état de l'instance.
        """
        super().__init__(request, client_address, server)
        MyRequestHandler.database=database

# les methodes sont abstraite statique donc je n'ai pas acces a database du constructeur

    def do_OPTIONS(self):
        """Gère la méthode HTTP OPTIONS.

        Cette méthode répond aux requêtes OPTIONS envoyées par le client pour connaître les méthodes supportées par l'API.

        Envoie un code de réponse 200 (OK) et les headers CORS (Cross-Origin Resource Sharing) pour autoriser les requêtes provenant de n'importe quelle origine (`Access-Control-Allow-Origin: *`).
        """
        print(f'OPTION : {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Allow-Methods','POST, PUT, GET, DELETE, OPTIONS')
        self.end_headers() 

    def do_GET(self):
        """Gère la méthode HTTP GET.

        Cette méthode gère les requêtes GET envoyées par le client pour récupérer des données.

        - Si le chemin d'accès est '/', elle appelle la fonction `getAll` pour récupérer tous les éléments de la base de données et renvoie les données en JSON.
        - Si le chemin d'accès contient un ID, elle essaie d'extraire l'ID et appelle la fonction `getOne` pour récupérer un élément spécifique en fonction de son ID. En cas d'erreur (ValueError ou IndexError), elle renvoie un code d'erreur 404 (NotFound).
        """
        print(f'GET : {self.path}')
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers() 
        # Extraire l'id si présent dans l'URL
        if self.path == '/':
            data = getAll(self.database)
        else:
            try:
                id = int(self.path.split('/')[-1])
                data = getOne(self.database,id)
            except (ValueError, IndexError):
                self.send_error(404)
                return
        print(f'data:{data}:')
        self.wfile.write(bytes(json.dumps(data), 'utf-8'))

    def do_POST(self):
        """Gère les requêtes HTTP POST pour créer une nouvelle ressource.

        Cette méthode extrait les données JSON du corps de la requête et les utilise pour créer un nouvel élément dans la base de données. 
        Envoie une réponse HTTP 201 (Créé) si la création est réussie, sinon une erreur 404 (Non trouvé).

        """
        print(f'POST : {self.path}')
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8')) 
        print(post_data)
        if create(self.database,post_data):
            self.send_response(201)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
        else:
            self.send_error(404)

    def do_PUT(self):
        """Gère les requêtes HTTP PUT pour mettre à jour une ressource existante.

        Cette méthode extrait l'ID de la ressource à mettre à jour à partir de l'URL et les nouvelles données à partir du corps de la requête. 
        Envoie une réponse HTTP 200 (OK) si la mise à jour est réussie, sinon une erreur 404 (Non trouvé).

        """
        print(f'PUT : {self.path}')
        # Extraire l'id et les données de la requête
        path_parts = self.path.split('/')
        if len(path_parts) < 1:
            self.send_error(404)
            return
        id = int(path_parts[1])
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        if update(self.database, data):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
        else:
            self.send_error(404)

    def do_DELETE(self):
        """Gère les requêtes HTTP DELETE pour supprimer une ressource existante.

        Cette méthode extrait l'ID de la ressource à supprimer à partir de l'URL. 
        Envoie une réponse HTTP 204 (Aucun contenu) si la suppression est réussie, sinon une erreur 404 (Non trouvé).

        """
        print(f'DELETE : {self.path}')
        # Extraire l'id de la requête
        path_parts = self.path.split('/')
        if len(path_parts) < 2:
            self.send_error(404)
            return
        id = int(path_parts[1])
        if delete(self.database,id):
            self.send_response(204)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_error(404)

def run_server(config):
    """Démarre un serveur HTTP en utilisant les paramètres de configuration fournis.

    Args:
        config (dict): Un dictionnaire contenant les paramètres de configuration du serveur, tels que le port et le chemin de la base de données.

    """
    with socketserver.TCPServer(("", config['server_port']), lambda request, client_address, server: MyRequestHandler(request, client_address, server, config['database'])) as httpd:
        print("Serving at port", config['server_port'])
        httpd.serve_forever()

def main():
    """Le point d'entrée principal de l'application."""
    # creation du handler pour les signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # lecture de la configuration
    config=read_config()
    # verification de la base de données
    version_bdd=read_version(config['database'])
    if version_bdd!=config['bddver']:
        updatebdd(config, version_bdd)
    # lancement du serveur API
    run_server(config)

if __name__ == "__main__":
    main()

app.run(host='0.0.0.0', port=8080)