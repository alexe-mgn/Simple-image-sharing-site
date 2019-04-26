import sqlite3 as sql


class LikesModel:
    con: sql.Connection

    def __init__(self, db):
        self.connect(db)
        self.create_table()

    def connect(self, db):
        """
        :type db: Database_likes
        """
        self.con = db.get_connection()

    def create_table(self):
        self.con.execute(
            '''
            CREATE TABLE if NOT EXISTS "likes" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            value INTEGER CHECK (1 <= value AND value <= 5),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.con.commit()

    def delete(self, id):
        self.con.execute('DELETE FROM likes WHERE id=?', (str(id),))
        self.con.commit()

    def find(self, **kwargs):
        c = self.con.cursor()
        q = 'SELECT * FROM likes WHERE ({})'.format(
            ' AND '.join('{}="{}"'.format(k, str(v)) for k, v in kwargs.items()))
        c.execute(q)
        r = c.fetchall()
        c.close()
        return r

    def get(self, id):
        c = self.con.cursor()
        c.execute('SELECT * FROM likes WHERE id=?', (str(id),))
        r = c.fetchone()
        c.close()
        return r

    def add(self, post_id, user_id):
        self.con.execute('INSERT INTO likes (post_id,  user_id) VALUES (?,?)',
                         (post_id, user_id))
        self.con.commit()

    def get_all(self):
        c = self.con.cursor()
        c.execute('SELECT * FROM likes')
        r = c.fetchall()
        c.close()
        return r

    def __getitem__(self, id):
        return self.get(id)

    def __delitem__(self, id):
        self.delete(id)
