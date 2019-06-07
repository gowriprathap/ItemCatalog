# -*- coding: utf-8 -*-
# Python program to add items to the catalog
from sqlalchemy import create_engine  # importing from SQL alchemy
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item, User
# importing tables from database_setup.py

engine = create_engine('sqlite:///itemcatalog.db')
# connecting to the database
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Menu for guitar
category1 = Category(name="Guitar")
# adding the first category guitar
session.add(category1)
session.commit()
# commit to the session

Item1 = Item(name="Electric Guitar",  # adding the items in guitar
             description="The electric guitar uses one or more pickups.",
             category=category1)
session.add(Item1)
session.commit()

Item2 = Item(name="Accoustic Guitar",  # adding items in guitar
             description="Transmit the vibration of the strings to the air.",
             category=category1)
session.add(Item2)
session.commit()

category2 = Category(name="Piano")  # adding the category piano
session.add(category2)
session.commit()


Item3 = Item(name="Grand Piano",  # adding the items in piano
             description="It uses the double escapement to play keys.",
             category=category2)
session.add(Item3)
session.commit()

Item4 = Item(name="Upright Piano",  # adding the items in piano
             description="The strings and the action are vertical.",
             category=category2)
session.add(Item4)
session.commit()

category3 = Category(name="Drums")  # adding category drums

session.add(category3)
session.commit()

Item5 = Item(name="Snare drum",  # adding the items in drums
             description="The snare drum produces a slight rattling sound.",
             category=category3)

session.add(Item5)
session.commit()

Item6 = Item(name="Bass drum",  # adding the items in drums
             description="The bass drum produces the lowest sounding beat.",
             category=category3)

session.add(Item6)
session.commit()


category4 = Category(name="Trumpet")  # adding the category trumpet

session.add(category4)
session.commit()

Item7 = Item(name="Cornet",  # adding the items in trumpet
             description="The cornet is distinguished by its conical bore.",
             category=category4)

session.add(Item7)
session.commit()

Item8 = Item(name="Flugelhorn",  # adding the items in trumpet
             description="The Flugelhorn resembles a normal trumpet.",
             category=category4)

session.add(Item8)
session.commit()


category5 = Category(name="Violin")  # adding the category violin

session.add(category5)
session.commit()

Item9 = Item(name="Accoustic violin",  # adding the items in violin
             description="It does not rely on electricity for playing.",
             category=category5)

session.add(Item9)
session.commit()

Item10 = Item(name="Electric violin",  # adding the items in violin
              description="Electric violins need a power source.",
              category=category5)

session.add(Item10)
session.commit()


category6 = Category(name="Flute")  # adding the category Flute

session.add(category6)
session.commit()

Item11 = Item(name="Piccolo",  # adding the items in flute
              description="It is used to make the melody with ornamentation.",
              category=category6)

session.add(Item11)
session.commit()

Item12 = Item(name="Alto Flute",  # adding the items in flute
              description="Its sound can create mysterious effects.",
              category=category6)

session.add(Item12)
session.commit()


category7 = Category(name="Clarinet")  # adding the category clarinet

session.add(category7)
session.commit()

Item13 = Item(name="Bb clarinet",  # adding the items in clarinet
              description="The most popular clarinet in the clarinet family.",
              category=category7)

session.add(Item13)
session.commit()

Item14 = Item(name="Bass clarinet",  # adding the items in clarinet
              description="The second most popular in the clarinet family.",
              category=category7)

session.add(Item14)
session.commit()


category8 = Category(name="Saxophone")  # adding the category saxophone

session.add(category8)
session.commit()

Item15 = Item(name="Tenor Saxophone:",  # adding the items in saxophone
              description="Widely played in rock and jazz music.",
              category=category8)

session.add(Item15)
session.commit()

Item16 = Item(name="Alto saxophone",  # adding the items in saxophone
              description="Generally regarded  for beginning students.",
              category=category8)

session.add(Item16)
session.commit()

print("Instruments added!")
# printing to the terminal to confirm that the Instruments have been added
