from datetime import datetime
from .base import Base
from sqlalchemy import Column, Integer, VARCHAR, DATE, String, BigInteger


class PostLandscaping(Base):
    __tablename__ = 'landscaping'
    post_id = Column(Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    user_id = Column(BigInteger, nullable=False)

    location = Column(String, nullable=False)
    description = Column(String, nullable=False)
    photo_id = Column(BigInteger, nullable=False)

    published = Column(DATE, default=datetime.today())
    status = Column(VARCHAR(50), nullable=False)

    def __call__(self, *args, **kwargs):
        return self.post_id

    def __str__(self):
        return f'Post: {self.post_id}'


class PostTransport(Base):
    __tablename__ = 'transport'
    post_id = Column(Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    user_id = Column(BigInteger, nullable=False)

    subcategory = Column(VARCHAR(50), nullable=False)
    number = Column(VARCHAR(50), nullable=False)
    description = Column(String, nullable=False)
    photo_id = Column(BigInteger, nullable=True)

    published = Column(DATE, default=datetime.today())
    status = Column(VARCHAR(50), nullable=False)

    def __call__(self, *args, **kwargs):
        return self.post_id

    def __str__(self):
        return f'Post: {self.post_id}'


class PostGarbage(Base):
    __tablename__ = 'garbage'
    post_id = Column(Integer, unique=True, autoincrement=True, nullable=False, primary_key=True)
    user_id = Column(BigInteger, nullable=False)

    location = Column(String, nullable=False)
    description = Column(String, nullable=False)
    photo_id = Column(BigInteger, nullable=False)

    published = Column(DATE, default=datetime.today())
    status = Column(VARCHAR(50), nullable=False)

    def __call__(self, *args, **kwargs):
        return self.post_id

    def __str__(self):
        return f'Post: {self.post_id}'
