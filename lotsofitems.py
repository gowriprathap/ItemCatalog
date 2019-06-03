# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, Item

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Menu for guitar
category1 = Category(name="Guitar")
session.add(category1)
session.commit()

Item1 = Item(name="Electric Guitar",
             description="The electric guitar uses one or more pickups.",
             category=category1)
session.add(Item1)
session.commit()

Item2 = Item(name="Accoustic Guitar",
             description="Transmit the vibration of the strings to the air.",
             category=category1)
session.add(Item2)
session.commit()

category2 = Category(name="Piano")
session.add(category2)
session.commit()


Item3 = Item(name="Grand Piano",
             description="It uses the double escapement to play keys.",
             category=category2)
session.add(Item3)
session.commit()

Item4 = Item(name="Upright Piano",
             description="The strings and the action are vertical.",
             category=category2)
session.add(Item4)
session.commit()

category3 = Category(name="Drums")

session.add(category3)
session.commit()

Item5 = Item(name="Snare drum",
             description="The snare drum produces a slight rattling sound.",
             category=category3)

session.add(Item5)
session.commit()

Item6 = Item(name="Bass drum",
             description="The bass drum produces the lowest sounding beat.",
             category=category3)

session.add(Item6)
session.commit()


category4 = Category(name="Trumpet")

session.add(category4)
session.commit()

Item7 = Item(name="Cornet",
             description="The cornet is distinguished by its conical bore.",
             category=category4)

session.add(Item7)
session.commit()

Item8 = Item(name="Flugelhorn",
             description="The Flugelhorn resembles a normal trumpet.",
             category=category4)

session.add(Item8)
session.commit()


category5 = Category(name="Violin")

session.add(category5)
session.commit()

Item9 = Item(name="Accoustic violin",
             description="It does not rely on electricity for playing.",
             category=category5)

session.add(Item9)
session.commit()

Item10 = Item(name="Electric violin",
              description="Electric violins need a power source.",
              category=category5)

session.add(Item10)
session.commit()


category6 = Category(name="Flute")

session.add(category6)
session.commit()

Item11 = Item(name="Piccolo",
              description="It is used to make the melody with ornamentation.",
              category=category6)

session.add(Item11)
session.commit()

Item12 = Item(name="Alto Flute",
              description="Its sound can create mysterious effects.",
              category=category6)

session.add(Item12)
session.commit()


category7 = Category(name="Clarinet")

session.add(category7)
session.commit()

Item13 = Item(name="Bb clarinet",
              description="The most popular clarinet in the clarinet family.",
              category=category7)

session.add(Item13)
session.commit()

Item14 = Item(name="Bass clarinet",
              description="The second most popular in the clarinet family.",
              category=category7)

session.add(Item14)
session.commit()


category8 = Category(name="Saxophone")

session.add(category8)
session.commit()

Item15 = Item(name="Tenor Saxophone:",
              description="Widely played in rock and jazz music.",
              category=category8)

session.add(Item15)
session.commit()

Item16 = Item(name="Alto saxophone",
              description="Generally regarded  for beginning students.",
              category=category8)

session.add(Item16)
session.commit()

print("Instruments added!")
