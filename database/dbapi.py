import getpass

from .models import *


class DatabaseConnector:

    def __init__(self):

        self.metadata = MetaData()
        self.engine = create_engine(f"postgresql+psycopg2://{getpass.getuser()}:@localhost:5432/{getpass.getuser()}")
        self.create_databases()

    def create_databases(self):

        self.books = get_books_model(self.metadata)
        self.borrows = get_borrows_model(self.metadata)

        self.metadata.create_all(self.engine)

    def get_book(self, data):

        connection = self.engine.connect()
        index = connection.execute(select(self.books.c.book_id).where(and_(
            func.lower(self.books.c.title) == func.lower(data['title']),
            func.lower(self.books.c.author) == func.lower(data['author']),
            self.books.c.published == data['published'],
            or_(
                self.books.c.date_deleted == None,
                self.books.c.date_deleted > data['date_point']
            )
        ))).fetchone()
        if index:
            return index[0]
        return False

    def add_book(self, data):

        connection = self.engine.connect()
        if self.get_book(data):
            return False
        data['date_added'] = data.pop('date_point')
        index = connection.execute(self.books.insert().values(
            data
        )).inserted_primary_key
        connection.commit()

        return index[0]

    def delete(self, data):

        connection = self.engine.connect()
        value = self.get_book(data)
        if not value or self.get_borrow_book(data):
            return False
        data['date_deleted'] = data.pop('date_point')
        connection.execute(update(self.books).where(and_(
            self.books.c.book_id == value
        )).values(
            data
        ))
        connection.commit()

        return True

    def list_books(self):

        connection = self.engine.connect()
        sel = connection.execute(select(self.books.c.title, self.books.c.author, self.books.c.published, self.books.c.date_deleted)).fetchall()
        res = ';\n'.join([', '.join(str(i) for i in list(x[:-1])) + (' (удалена)' if x[-1] else '') for x in sel])
        return res+';'


    def get_borrow(self, data):

        connection = self.engine.connect()
        index = connection.execute(select(self.borrows.c.user_id).where(and_(
            self.borrows.c.user_id == data['user_id'],
            self.borrows.c.date_start < data['date_point'],
            or_(
                data['date_point'] < self.borrows.c.date_end,
                self.borrows.c.date_end == None
            )
        ))).fetchone()
        if index:
            return index[0]
        return False

    def get_borrow_book(self, data):

        connection = self.engine.connect()
        book_id = int(self.get_book(data))
        index = connection.execute(select(self.borrows.c.book_id).where(and_(
            self.borrows.c.book_id == book_id,
            self.borrows.c.date_start < data['date_point'],
            or_(
                data['date_point'] < self.borrows.c.date_end,
                self.borrows.c.date_end == None
            )
        ))).fetchone()
        if index:
            return index[0]
        return False

    def borrow(self, data):

        connection = self.engine.connect()
        if self.get_borrow(data) or self.get_borrow_book(data):
            return False
        data['book_id'] = self.get_book(data)
        data['date_start'] = data.pop('date_point')
        data.pop('title'), data.pop('author'), data.pop('published')
        index = connection.execute(self.borrows.insert().values(
            data
        )).inserted_primary_key
        connection.commit()

        return index[0]

    def retrieve(self, data):

        connection = self.engine.connect()
        data['date_end'] = data.pop('date_point')
        book_data = connection.execute(
            select(self.books.c.book_id, self.books.c.title, self.books.c.author, self.books.c.published).select_from(
                self.borrows.join(self.books, self.borrows.c.book_id == self.books.c.book_id)).where(and_(
                self.borrows.c.user_id == data['user_id'],
                self.borrows.c.date_end == None
            ))).fetchall()
        if not book_data:
            return False
        book_data = book_data[0]
        connection.execute(update(self.borrows).where(and_(
            self.borrows.c.book_id == book_data[0]
        )).values(
            data
        ))
        connection.commit()

        return book_data[1:]

    def find_stat(self, data):

        connection = self.engine.connect()
        book_data = connection.execute(
            select(self.books.c.book_id, self.books.c.title, self.books.c.author, self.books.c.published,
                   self.borrows.c.date_start, self.borrows.c.date_end).select_from(
                self.borrows.join(self.books, self.borrows.c.book_id == self.books.c.book_id)).where(and_(
                func.lower(self.books.c.title) == func.lower(data['title']),
                func.lower(self.books.c.author) == func.lower(data['author']),
                self.books.c.published == data['published']
            ))).fetchall()

        return book_data[0][0] if book_data else False

    def get_stat(self, data):

        connection = self.engine.connect()
        book_data = connection.execute(
            select(self.books.c.book_id, self.books.c.title, self.books.c.author, self.books.c.published, self.borrows.c.date_start, self.borrows.c.date_end).select_from(
                self.borrows.join(self.books, self.borrows.c.book_id == self.books.c.book_id)).where(and_(
                self.books.c.book_id == data['book_id']
            ))).fetchall()

        return book_data
