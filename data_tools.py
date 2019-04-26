import sqlite3 as sql
import random
import os


class Database:
    con: sql.Connection

    def __init__(self, path):
        self.con = None
        dr = os.path.split(path)[0]
        if dr and not os.path.isdir(dr):
            os.mkdir(dr)
        self.connect(path)
        self.con.row_factory = sql.Row

    def connect(self, path):
        self.con = sql.connect(path, check_same_thread=False)

    def disconnect(self):
        if self.con is not None:
            self.con.close()
            self.con = None

    def get_connection(self):
        return self.con

    connection = property(get_connection)

    def __del__(self):
        self.disconnect()


class UsersModel:
    con: sql.Connection

    def __init__(self, db):
        self.connect(db)
        self.create_table()

    def connect(self, db):
        """
        :type db: Database
        """
        self.con = db.get_connection()

    def create_table(self):
        self.con.execute('''
        CREATE TABLE if NOT EXISTS "users" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(50),
        password VARCHAR(128),
        time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
        )
        ''')
        self.con.commit()

    def del_user(self, id):
        self.con.execute('DELETE FROM users WHERE id=?', (str(id),))
        self.con.commit()

    def user_exists(self, id):
        c = self.con.cursor()
        c.execute('''
        SELECT * FROM users WHERE id=?
        ''', (id,))
        r = bool(c.fetchall())
        c.close()
        return r

    def find_user(self, **kwargs):
        c = self.con.cursor()
        q = 'SELECT * FROM users WHERE ({})'.format(
            ' AND '.join('{}="{}"'.format(k, str(v)) for k, v in kwargs.items()))
        c.execute(q)
        r = c.fetchall()
        c.close()
        return r

    def get_user(self, id):
        c = self.con.cursor()
        c.execute('SELECT * FROM users WHERE id=?', (str(id),))
        r = c.fetchone()
        c.close()
        return r

    def edit_user(self, id, **kwargs):
        if len(kwargs) < 1:
            return
        keys = kwargs.keys()
        self.con.execute('''
        UPDATE users SET {} WHERE id=?
        '''.format(', '.join(k + '=?' for k in keys)), (*[kwargs[k] for k in keys], id))

    def add_user(self, name, password):
        self.con.execute('INSERT INTO users (name, password) VALUES (?,?)', (name, password))
        self.con.commit()

    def get_all(self):
        c = self.con.cursor()
        c.execute('SELECT * FROM users')
        r = c.fetchall()
        c.close()
        return r

    def __getitem__(self, id):
        return self.get_user(id)

    def __delitem__(self, id):
        self.del_user(id)
