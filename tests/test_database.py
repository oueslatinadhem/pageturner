import unittest
import sqlite3
import json
import tempfile
import os
from api.server import getAll, getOne, create, update, delete  # Remplacer 'your_module' par le nom de votre module

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Créer une base de données en mémoire pour les tests
        self.db_file = tempfile.NamedTemporaryFile(delete=False)
        self.conn = sqlite3.connect(self.db_file.name)
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE data (id INTEGER PRIMARY KEY AUTOINCREMENT, titre VARCHAR(1024) NOT NULL, detail TEXT)")
        self.conn.commit()
        self.cur.execute("INSERT INTO data (titre, detail) VALUES (?, ?)", ("Titre 1", "Détail 1"))
        self.conn.commit()

    def tearDown(self):
        self.conn.close()
        os.remove(self.db_file.name)

    # Tests pour la fonction getAll
    def test_getAll(self):
        # Insérer quelques données
        result = getAll(self.db_file.name)
        self.assertIsNotNone(result)
        data = json.loads(result)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['titre'], "Titre 1")

    # Tests pour la fonction getOne
    def test_getOne(self):
        # Insérer quelques données
        result = getOne(self.db_file.name,1)
        self.assertIsNotNone(result)
        data = json.loads(result)
        self.assertEqual(data['titre'], "Titre 1")
        self.assertEqual(data['detail'], "Détail 1")
        
    # Tests pour la fonction create
    def test_create(self):
        # Insérer quelques données
        result = create(self.db_file.name,{"titre":"Titre 2","detail":"Détail 2"})
        self.assertEqual(result, True)
        if result :
            result = getOne(self.db_file.name,2)
            self.assertIsNotNone(result)
            data = json.loads(result)
            self.assertEqual(data['titre'], "Titre 2")
            self.assertEqual(data['detail'], "Détail 2")
        
    # Tests pour la fonction update
    def test_update(self):
        # Insérer quelques données
        result = update(self.db_file.name,{"id":1,"titre":"Titre 2","detail":"Détail 2"})
        self.assertEqual(result, True)
        if result :
            result = getOne(self.db_file.name,1)
            self.assertIsNotNone(result)
            data = json.loads(result)
            self.assertEqual(data['titre'], "Titre 2")
            self.assertEqual(data['detail'], "Détail 2")
        
    # Tests pour la fonction delete
    def test_delete(self):
        # Insérer quelques données
        result = delete(self.db_file.name,1)
        self.assertEqual(result, True)
        if result :
            result = getAll(self.db_file.name)
            self.assertIsNotNone(result)
            data = json.loads(result)
            self.assertEqual(len(data), 0)
        

if __name__ == '__main__':
    unittest.main()