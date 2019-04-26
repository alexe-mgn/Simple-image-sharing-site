import sqlite3 as sql
import os


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
        self.con.execute(
            '''
            CREATE TABLE if NOT EXISTS "users" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50),
            password VARCHAR(128),
            nickname VARCHAR(50),
            id_avatar INTEGER,
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.con.commit()

    def delete(self, id):
        self.con.execute('DELETE FROM users WHERE id=?', (str(id),))
        self.con.commit()

    def find(self, **kwargs):
        c = self.con.cursor()
        q = 'SELECT * FROM users WHERE ({})'.format(
            ' AND '.join('{}="{}"'.format(k, str(v)) for k, v in kwargs.items()))
        c.execute(q)
        r = c.fetchall()
        c.close()
        return r

    def get(self, id):
        c = self.con.cursor()
        c.execute('SELECT * FROM users WHERE id=?', (str(id),))
        r = c.fetchone()
        c.close()
        return r

    def edit(self, id, **kwargs):
        if len(kwargs) < 1:
            return
        keys = kwargs.keys()
        self.con.execute('''
        UPDATE users SET {} WHERE id=?
        '''.format(', '.join(k + '=?' for k in keys)), (*[kwargs[k] for k in keys], id))

    def add(self, name, nickname, password, id_avatar=0):
        self.con.execute('INSERT INTO users (name,  password, nickname, id_avatar) VALUES (?,?,?,?)',
                         (name, nickname, password, id_avatar))
        self.con.commit()

    def get_all(self):
        c = self.con.cursor()
        c.execute('SELECT * FROM users')
        r = c.fetchall()
        c.close()
        return r

    def __getitem__(self, id):
        return self.get(id)

    def __delitem__(self, id):
        self.delete(id)
