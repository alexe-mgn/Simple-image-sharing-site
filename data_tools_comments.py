import sqlite3 as sql


class CommentsModel:
    con: sql.Connection

    def __init__(self, db):
        self.connect(db)
        self.create_table()

    def connect(self, db):
        """
        :type db: Database_comments
        """
        self.con = db.get_connection()

    def create_table(self):
        self.con.execute(
            '''
            CREATE TABLE if NOT EXISTS "comments" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            post_id INTEGER,
            text VARCHAR(2048),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.con.commit()

    def delete(self, id):
        self.con.execute('DELETE FROM comments WHERE id=?', (str(id),))
        self.con.commit()

    def find(self, **kwargs):
        c = self.con.cursor()
        q = 'SELECT * FROM comments WHERE ({})'.format(
            ' AND '.join('{}="{}"'.format(k, str(v)) for k, v in kwargs.items()))
        c.execute(q)
        r = c.fetchall()
        c.close()
        return r

    def get(self, id):
        c = self.con.cursor()
        c.execute('SELECT * FROM comments WHERE id=?', (str(id),))
        r = c.fetchone()
        c.close()
        return r

    def edit(self, id, **kwargs):
        if len(kwargs) < 1:
            return
        keys = kwargs.keys()
        self.con.execute(
            '''
            UPDATE comments SET {} WHERE id=?
            '''.format(', '.join(k + '=?' for k in keys)), (*[kwargs[k] for k in keys], id))

    def add(self, user_id, post_id, text):
        self.con.execute('INSERT INTO comments (user_id,  post_id, text) VALUES (?,?,?)', (user_id, post_id, text))
        self.con.commit()

    def get_all(self):
        c = self.con.cursor()
        c.execute('SELECT * FROM comments')
        r = c.fetchall()
        c.close()
        return r

    def __getitem__(self, id):
        return self.get(id)

    def __delitem__(self, id):
        self.delete(id)
