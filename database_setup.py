from sqlalchemy import Column, ForeignKey, Integer, String #importing from sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base() #making an instance of the declarative_base class we just imported


class User(Base): #creating class User
    __tablename__ = 'user' #representation of the table in our database

    id = Column(Integer, primary_key=True)
    name = Column(String(32), index=True) #maps python objects to columns in the database
    picture = Column(String)
    email = Column(String)


class Category(Base): #creating class category
    __tablename__ = 'category' #representation of the table in our database

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False) #maps python objects to columns in the database
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
           }


class Item(Base): #creating class item
    __tablename__ = 'item' #representation of the table in our database

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250)) #maps python objects to columns in the database
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User) # specifying relationship with the user class

    @property
    def serialize(self):
        return {
            'category_id': self.category_id,
            'id': self.id,
            'name': self.name,
            'description': self.description,
            }


engine = create_engine('sqlite:///itemcatalog.db') # This creates the empty database
Base.metadata.create_all(engine)
