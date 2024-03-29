import sqlite3 as sql
import os


class Database:
    connection: sql.Connection

    def __init__(self, path):
        self.connection = None
        dr = os.path.split(path)[0]
        if dr and not os.path.isdir(dr):
            os.mkdir(dr)
        self.connect(path)
        self.connection.row_factory = sql.Row

    def connect(self, path):
        self.connection = sql.connect(path, check_same_thread=False)

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def get_connection(self):
        return self.connection

    con = property(get_connection)

    def __del__(self):
        self.disconnect()


class ResourceModel:

    def __init__(self, db, table):
        self.connect(db)
        self.table = table
        self.create_table()

    def connect(self, db):
        """
        :type db: Database
        """
        self.db = db
        self.connection = db.get_connection()

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS {} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            '''.format(self.table))
        self.connection.commit()

    def columns(self):
        return 'id', 'time'

    def delete(self, id):
        self.connection.execute('DELETE FROM {} WHERE id=?'.format(self.table), (id,))
        self.connection.commit()

    def find(self, **kwargs):
        items = kwargs.items()
        c = self.connection.cursor()
        q = 'SELECT * FROM {} WHERE ({})'.format(
            self.table,
            ' AND '.join('{}=?'.format(e[0]) for e in items)
        )
        c.execute(q, (*[e[1] for e in items],))
        r = c.fetchall()
        c.close()
        return r

    def get(self, id):
        c = self.connection.cursor()
        c.execute('SELECT * FROM {} WHERE id=?'.format(self.table), (id,))
        r = c.fetchone()
        c.close()
        return r

    def edit(self, id, **kwargs):
        if len(kwargs) < 1:
            return
        items = kwargs.items()
        self.connection.execute(
            '''
            UPDATE {} SET {} WHERE id=?
            '''.format(
                self.table,
                ', '.join('{}=?'.format(e[0]) for e in items)
            ),
            (*[e[1] for e in items], id))
        self.connection.commit()

    def add(self, *args, **kwargs):
        if args:
            self.connection.execute(
                'INSERT INTO {} VALUES ({})'.format(
                    self.table,
                    ', '.join('?' for _ in range(len(args) + 1))
                ),
                (self.max_id() + 1, *args)
            )
        else:
            items = kwargs.items()
            self.connection.execute(
                'INSERT INTO {} ({}) VALUES ({})'.format(
                    self.table,
                    ', '.join(e[0] for e in items),
                    ','.join('?' for _ in range(len(items)))
                ),
                (*[e[1] for e in items],)
            )
        self.connection.commit()
        return self.last_row()['id']

    def get_all(self):
        c = self.connection.cursor()
        c.execute('SELECT * FROM {}'.format(self.table))
        r = c.fetchall()
        c.close()
        return r

    def max_id(self):
        c = self.connection.cursor()
        c.execute('SELECT max(id) FROM {}'.format(self.table))
        r = c.fetchone()
        c.close()
        return r

    def last_row(self):
        c = self.connection.cursor()
        c.execute('SELECT * FROM {0} WHERE time = (SELECT max(time) FROM {0})'.format(self.table))
        r = c.fetchone()
        c.close()
        return r

    def exists(self, id):
        c = self.connection.cursor()
        c.execute('SELECT * FROM {} WHERE id=?'.format(self.table), (id,))
        r = bool(c.fetchone())
        c.close()
        return r

    def __getitem__(self, id):
        return self.get(id)

    def __delitem__(self, id):
        self.delete(id)


class UsersModel(ResourceModel):

    def __init__(self, db):
        super().__init__(db, 'users')

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login VARCHAR(50),
            password VARCHAR(128),
            name VARCHAR(50) DEFAULT NULL,
            avatar_id INTEGER DEFAULT 0,
            info VARCHAR(2048) DEFAULT 'Нет информации' NOT NULL,
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.connection.execute(
            '''
            CREATE TRIGGER IF NOT EXISTS user_default_name AFTER INSERT ON users
            WHEN new.name ISNULL
            BEGIN
                UPDATE users
                SET name = new.login
                WHERE id = new.id;
            END;
            ''')
        self.connection.execute('CREATE TABLE IF NOT EXISTS admins (user_id INTEGER)')
        self.connection.commit()

    def login_exists(self, login):
        c = self.connection.cursor()
        c.execute('SELECT * FROM users WHERE login=?', (login,))
        r = bool(c.fetchone())
        c.close()
        return r

    def is_admin(self, uid):
        c = self.connection.cursor()
        c.execute('SELECT * FROM admins WHERE user_id=?', (uid,))
        r = c.fetchone()
        c.close()
        return bool(r)

    def set_admin(self, uid):
        self.connection.execute(
            '''
            INSERT INTO admins (user_id) SELECT id FROM users WHERE id=?
            ''', (uid,))
        self.connection.commit()


class ImagesModel(ResourceModel):

    def __init__(self, db):
        super().__init__(db, 'images')

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename VARCHAR(512),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.connection.commit()

    def upload_secure(self, bytes, name):
        bn, ext = os.path.splitext(name)
        fnp = os.path.join('static\\img', bn)
        n = 0
        while os.path.isfile(fnp + str(n) + ext):
            n += 1
        fp = fnp + str(n) + ext
        with open(fp, mode='wb') as out:
            out.write(bytes)
        self.add(filename=(bn + str(n) + ext).replace('\\', '/'))
        self.connection.commit()
        return self.last_row()['id']

    def delete(self, id):
        img = self.get(id)
        if img:
            fp = os.path.join('static\\img', img['filename'])
            if os.path.isfile(fp):
                os.remove(fp)
        super().delete(id)


class PublicationsModel(ResourceModel):

    def __init__(self, db):
        super().__init__(db, 'posts')

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_id INTEGER,
            text VARCHAR(2048),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.connection.commit()

    def delete(self, id):
        data = self.get(id)
        self.connection.execute('DELETE FROM likes WHERE post_id=?', (id,))
        self.connection.execute('DELETE FROM comments WHERE post_id=?', (id,))
        ImagesModel(self.db).delete(data['image_id'])
        super().delete(id)


class CommentsModel(ResourceModel):

    def __init__(self, db):
        super().__init__(db, 'comments')

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            text VARCHAR(2048),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.connection.commit()


class LikesModel(ResourceModel):

    def __init__(self, db):
        super().__init__(db, 'likes')

    def create_table(self):
        self.connection.execute(
            '''
            CREATE TABLE if NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            value INTEGER CHECK (1 <= value AND value <= 6),
            time INTEGER DEFAULT (cast(strftime('%s', 'now') as INTEGER))
            )
            ''')
        self.connection.commit()

    def get_rating(self, pid):
        c = self.connection.cursor()
        c.execute('SELECT avg(value) FROM likes WHERE (post_id=?)', (pid,))
        r = c.fetchone()[0]
        c.close()
        return r if r is not None else 0

    def get_user_rating(self, pid, uid):
        c = self.connection.cursor()
        c.execute('SELECT value FROM likes WHERE (post_id=? AND user_id=?)', (pid, uid))
        r = c.fetchone()
        c.close()
        return r[0] if r is not None else 0

    def user_rated(self, pid, uid):
        c = self.connection.cursor()
        c.execute('SELECT * FROM likes WHERE (post_id=? AND user_id=?)', (pid, uid))
        r = c.fetchone()
        c.close()
        return r is not None

    def rate(self, pid, uid, value):
        if value <= 0:
            self.connection.execute('DELETE FROM likes WHERE (post_id=? AND user_id=?)', (pid, uid))
        else:
            if value > 6:
                value = 6
            args = {'pid': pid, 'uid': uid, 'val': value}
            self.connection.execute(
                '''
                INSERT OR IGNORE INTO likes (id, post_id, user_id, value)
                    VALUES (
                    (SELECT id FROM likes WHERE (post_id=:pid AND user_id=:uid)),
                    :pid,
                    :uid,
                    1
                    )
                ''', args)
            self.connection.execute(
                '''
                UPDATE likes
                 SET post_id=:pid, user_id=:uid, value=:val, time=(cast(strftime('%s', 'now') as INTEGER))
                  WHERE (post_id=:pid AND user_id=:uid AND NOT value=:val)
                ''', args)
        self.connection.commit()
