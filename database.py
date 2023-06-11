import random
import json
import sqlite3
import requests
import urllib.request

class SnippetsDatabase:
    """Class for managing SQLite database"""

    def __init__(self, db_name: str = "snippets.db"):
        self.db_name: str = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

        self.current_user = None

        self.create_tables()

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def get_total_users(self):
        """Returns the total number of users"""
        self.execute_query("SELECT COUNT(*) FROM users")
        return self.fetch_one()[0]

    def get_total_snippets(self):
        """Returns the total number of snippets"""
        self.execute_query("SELECT COUNT(*) FROM snippets")
        return self.fetch_one()[0]

    def get_total_supported_languages(self):
        """Returns the total number of supported languages"""
        self.execute_query("SELECT COUNT(*) FROM supported_languages")
        return self.fetch_one()[0]


    def get_snippets_count_by_language(self):
        """Returns the count of snippets for each language"""
        self.execute_query("SELECT language, COUNT(*) FROM snippets GROUP BY language")
        return self.fetch_all()

    def get_snippets_count_by_user(self):
        """Returns the count of snippets for each user"""
        self.execute_query("SELECT user_id, COUNT(*) FROM snippets GROUP BY user_id")
        return self.fetch_all()


    def execute_query(self, query, params=None):
        """Executes a query with optional parameters"""
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

    def run_and_get_output(self, query, params=None):
        """Executes a query and returns the output"""
        self.execute_query(query, params)
        return self.fetch_all()

    def fetch_all(self):
        """Fetches all results from the last executed query"""
        return self.cursor.fetchall()

    def fetch_one(self):
        """Fetches one result from the last executed query"""
        return self.cursor.fetchone()

    def create_users_table(self):
        """Creates the users table"""
        self.execute_query("""CREATE TABLE IF NOT EXISTS "users" (
            "id"	INTEGER NOT NULL UNIQUE,
            "username"	TEXT NOT NULL UNIQUE,
            "password"	TEXT,
            "access_code"	INTEGER DEFAULT 1,
            PRIMARY KEY("id" AUTOINCREMENT)
        )""")
        # Add an administrator if the table is empty
        self.execute_query("SELECT * FROM users")
        if not self.fetch_all():
            self.add_user("admin", "admin", 2)

    def create_snippets_table(self):
        """Creates the snippets table"""
        self.execute_query("""CREATE TABLE IF NOT EXISTS "snippets" (
            "id"	INTEGER,
            "name"	TEXT,
            "language"	TEXT,
            "code"	TEXT,
            "example_code"	TEXT,
            "stdin"	TEXT,
            "expected_output"	TEXT,
            "is_private"	INTEGER,
            "user_id"	INTEGER NOT NULL,
            PRIMARY KEY("id")
        )""")

    def create_supported_languages_table(self):
        """Creates the supported_languages table"""
        self.execute_query("""CREATE TABLE IF NOT EXISTS "supported_languages" (
            "id"	INTEGER NOT NULL UNIQUE,
            "name"	TEXT NOT NULL
        )""")
        self.update_supported_languages()

    def is_admin(self, user_id: int):
        """Checks if the user is an administrator"""
        self.execute_query("SELECT access_code FROM users WHERE id = ?", (user_id,))
        return self.fetch_one()[0] == 2
        
    def create_tables(self):
        """Creates all tables"""
        self.create_users_table()
        self.create_snippets_table()
        self.create_supported_languages_table()

    def add_user(self, username: str, password: str, access_code: int = 1):
        """Adds a user to the users table"""
        self.execute_query("INSERT INTO users VALUES (NULL, ?, ?, ?)", (username, password, access_code))
        self.connection.commit()

    def add_snippet(self, name: str, language: str, code: str, example_code: str, stdin: str,
                    expected_output: str, is_private: bool):
        """Adds a snippet to the snippets table"""
        if self.current_user > 0:
            self.execute_query("INSERT INTO snippets VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)",
                               (name, language, code, example_code, stdin, expected_output, is_private, self.current_user))
            self.connection.commit()
        else:
            raise Exception("Anonymous users cannot add snippets")
    
    def edit_snippet(self, snippet_id, name=None, language=None, code=None, example_code=None, stdin=None,
                    expected_output=None, is_private=None):
        """Edits a snippet in the snippets table"""
        if self.current_user > 0:
            self.execute_query("UPDATE snippets SET name = ?, language = ?, code = ?, example_code = ?, stdin = ?, expected_output = ?, is_private = ? WHERE id = ?",
                               (name, language, code, example_code, stdin, expected_output, is_private, snippet_id))
            self.connection.commit()
        else:
            raise Exception("Anonymous users cannot edit snippets")

    # def get_public_snippets(self):
    #     """Returns a list of public snippets"""
    #     self.execute_query("SELECT * FROM snippets WHERE is_private = 0")
    #     return self.fetch_all()

    def get_snippets(self, user_id: int = 0):
        """Returns all snippets from the snippets table"""
        if user_id > 0:
            self.execute_query("SELECT * FROM snippets WHERE user_id = ? OR is_private = 0", (user_id,))
        else:
            self.execute_query("SELECT * FROM snippets WHERE is_private = 0")
        return self.fetch_all()

    def get_snippet(self, snippet_id: int):
        """Returns a snippet from the snippets table by id"""
        self.execute_query("SELECT * FROM snippets WHERE id = ?", (snippet_id,))
        return self.fetch_one()

    def update_snippet(self, snippet_id: int, name: str, language: str, code: str):
        """Updates a snippet in the snippets table"""
        self.execute_query("UPDATE snippets SET name = ?, language = ?, code = ? WHERE id = ?",
                           (name, language, code, snippet_id))
        self.connection.commit()

    def delete_snippet(self, snippet_id: int):
        """Deletes a snippet from the snippets table"""
        self.execute_query("DELETE FROM snippets WHERE id = ?", (snippet_id,))
        self.connection.commit()

    def get_user(self, user_id: int):
        """Returns a user from the users table by id"""
        self.execute_query("SELECT * FROM users WHERE id = ?", (user_id,))
        return self.fetch_one()

    def get_user_by_username(self, username: str):
        """Returns a user from the users table by username"""
        self.execute_query("SELECT * FROM users WHERE username = ?", (username,))
        return self.fetch_one()

    def login(self, username: str, password: str):
        """Authorizes a user"""
        user = self.get_user_by_username(username)
        if user and user[2] == password:
            self.current_user = user[0]
            return True
        else:
            return False

    def logout(self):
        """Deauthorizes a user"""
        self.current_user = 0

    def register(self, username: str, password: str):
        """Registers a user"""
        if self.get_user_by_username(username):
            return False
        else:
            self.add_user(username, password)
            return True

    def update_supported_languages(self):
        """Updates the supported_languages table with languages from Judge0 API"""
        self.execute_query("DELETE FROM supported_languages")
        response = requests.get('https://ce.judge0.com/languages/', timeout=5)
        response.raise_for_status()
        languages = response.json()
        for language in languages:
            self.execute_query("INSERT INTO supported_languages VALUES (?, ?)",
                               (language['id'], language['name']))
        self.connection.commit()

    def get_supported_languages(self):
        """Returns all supported programming languages"""
        self.execute_query("SELECT * FROM supported_languages")
        return self.fetch_all()

    def get_supported_language(self, language_id: int):
        """Returns a supported programming language by id"""
        self.execute_query("SELECT * FROM supported_languages WHERE id = ?", (language_id,))
        return self.fetch_one()
    
    
    def get_all_users(self):
        self.execute_query("SELECT * FROM users")
        users = self.fetch_all()
        return users
    
    def generate_random_users(self):
        url = "https://fakerapi.it/api/v1/users?_quantity=10&_locale=uk_UA"
        
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            users = data['data']
            for user in users:
                self.add_user(user['username'], user['password'], random.randint(1, 2))


