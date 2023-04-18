from sqlalchemy import *


def get_books_model(metadata):

    return Table(
        'Books',
        metadata,
        Column('book_id', Integer(), Identity(start=1, cycle=True), primary_key=True),
        Column('title', String(50), nullable=False),
        Column('author', String(100)),
        Column('published', Integer()),
        Column('date_added', Date(), nullable=False),
        Column('date_deleted', Date())
    )


def get_borrows_model(metadata):

    return Table(
        'Borrows',
        metadata,
        Column('borrow_id', Integer(), Identity(start=1, cycle=True), primary_key=True),
        Column('book_id', Integer(), nullable=False),
        Column('date_start', DateTime(), nullable=False),
        Column('date_end', DateTime()),
        Column('user_id', BIGINT(), nullable=False)
    )
