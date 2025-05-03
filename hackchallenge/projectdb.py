#db.py
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable to avoid warnings
db = SQLAlchemy(app)

# db = SQLAlchemy()

import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


# Menu items of all the dining halls
# Photos of the plates
# User preferences are determined whenever you open the app
# Create accounts and login (User authentication) / Delete accounts
# figure out how to do matching. (ratings can be made thru some sorting implementation)
    #Matching system (like recommending based on ratings or preferences)


# use a file to populate
menus_table = db.Table(
    'menus',
    db.Column('dining_hall',db.Integer, db.ForeignKey("dininghall.id"), primary_key=True), # c
    db.Column('menu_items', db.Integer, db.ForeignKey("menuitem.id"), primary_key=True)
)
    

# Many to many relationship between menu and menu items
# This table is used to link menu items to menus
menu_menuitem = db.Table(
    "menu_menuitem",
    db.Column("menu_id", db.Integer, db.ForeignKey("menu.id"), primary_key=True), #menu
    db.Column("menuitem_id", db.Integer, db.ForeignKey("menuitem.id"), primary_key=True) #menu item
)

class User(db.Model):
    """
    User model
    One-to-one relationship with unique user account information
    """
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    username = db.Column(db.String, unique =True, nullable = False)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True, nullable = False)
    passwordHash = db.Column(db.String, nullable = False)

    swipes = db.relationship("Swipe", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email
        }
    
class UserSwipeTable(db.Model):
    """
    User swipe table model
    Many to many relationship with user and dining hall
    """
    __tablename__="user_swipe_table"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True) 
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    
    SwipeNumber = db.Column(db.Integer, nullable = False)
    menuItemId = db.Column(db.Integer, db.ForeignKey("menuitem.id"), nullable=False)
    swipeStatus = db.Column(db.Boolean, nullable = False) #right:true left:false

    user = db.relationship("User", backref="user_swipe_table_entries")
    menu_item = db.relationship("MenuItem", backref="user_swipes")

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "SwipeNumber": self.SwipeNumber,
            "menuItemId": self.menuItemId,
            "swipeStatus": self.swipeStatus
        }
    
class Swipe(db.Model): 
    """
    User swiping model to provide the student a dining hall 

    Many to one relationship, many swipes for one user
    """
    __tablename__="swipe"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    menuId= db.Column(db.Integer, db.ForeignKey("menu.id"), nullable = False)
    swipeBoolean = db.Column(db.Boolean, nullable=False) #right:true left:false

    user = db.relationship("User", back_populates="swipes")
    menu_item = db.relationship("MenuItem", back_populates="swipes")
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menuitem.id"))


    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "menuId": self.menuId,
            "swipeBoolean": self.swipeBoolean
        }
    
# class PlatePhotos(db.Model):
#         """
#         Plate uploading model (Create/Update)
        
#         Users upload a photo of the plate, name of dish, last time created will be listed
#         details of the plate will be provided in database

#         Many to one relationship with dininghall and menu
#         """
#         __tablename__="plate"
#         id = db.Column(db.Integer, primary_key=True, autoincrement = True)
#         menuItemId= db.Column(db.Integer, db.ForeignKey("menu.id"), nullable = False)
#         diningHallId= db.Column(db.Integer, db.ForeignKey("dininghall.id"), nullable = False)

#         timeCreated = db.Column(db.DateTime, server_default= db.func.now())
#         menu_item = db.relationship("Menu", backref = "plates") # many plates
#         dining_hall = db.relationship("DiningHall", backref = "plates") # many plates

#         photo = db.Column(db.String)

#         def serialize(self):
#             return {
#                 "id": self.id,
#                 "menuItemId": self.menuItemId,
#                 "diningHallId": self.diningHallId,
#                 "timeCreated": self.timeCreated.isoformat(),
#                 "photo": self.photo
#             }



class Menu(db.Model):
    """
    Menu model; information for all plates
    One to many relationships with PlatePhotos
    """
    __tablename__="menu"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    dininghallId= db.Column(db.Integer, db.ForeignKey("dininghall.id"), nullable = False)
    name = db.Column(db.String, nullable = False) 
    description = db.Column(db.String)
    
    # photo = db.Column(db.String, db.ForeignKey("plate.photo"), nullable=True)
    # preferenceTags =  db.Column(db.String)
    menu_items = db.relationship("MenuItem", secondary=menu_menuitem, back_populates="menus")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "dininghallId": self.dininghallId,
            "description": self.description,
            # "photo": self.photo,
            # "preferenceTags": self.preferenceTags
        }

class MenuItem(db.Model):
    """
    Menu item model
    Many to many relationship with Menu
    """
    __tablename__="menuitem"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String, nullable = False) 
    description = db.Column(db.String)
    photo = db.Column(db.String)

    swipes = db.relationship("Swipe", back_populates="menu_item")
    menus = db.relationship("Menu", secondary=menu_menuitem, back_populates="menu_items")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "photo": self.photo,
            "menuIds": [menu.id for menu in self.menus]
        }


class DiningHall(db.Model):
    """
    Dining Hall model
    One to many relationship with items on the menu for each dining hall
    """

    __tablename__="dininghall"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    name = db.Column(db.String)
    # location = db.Column(db.String)

    # startinghour = db.Column(db.String)
    # endinghour = db.Column(db.String)
    # latitude = db.Column(db.Float)
    # longitude = db.Column(db.Float)
    swipeCount = db.Column(db.Integer, default=0)

    menu_items = db.relationship('MenuItem', secondary=menus_table, backref='dininghalls') # class name first, not table name
    # a menuitem object can access item.dining_halls to get the dining hall objects linked to it

    menus = db.relationship("Menu", backref="dining_hall", lazy=True)

    def calculate_distance(self, user_latitude, user_longitude):
        """
        Calculate the distance of each dining hall to user's location
        """
        if self.latitude is None or self.longitude is None:
            return None
        radius_of_earth = 3958.8 #miles
        lat1= radians(self.latitude)
        long1 = radians(self.longitude)

        lat2 = radians(user_latitude)
        long2 = radians(user_longitude)

        difference_lat = lat2 - lat1
        difference_long = long2 - long1

        a = sin(difference_lat / 2)**2 + cos(lat1) * cos(lat2) * sin(difference_long / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return radius_of_earth * c  # Distance in miles

    def serialize(self, user_latitude = None, user_longitude = None):
        """
        Serialize dining hall data and distance if user coordinates are given (should always be given)
        
        user_latitude: float of User's latitude
        user_longitude: float of User's longitude
        """
        return {
            "id": self.id,
            "name": self.name,
            # "location": self.location,
            # "latitude":self.latitude,
            # "longitude": self.longitude,
            # "startinghour":self.startinghour,
            # "endinghour": self.endinghour,
            "menu": [menu.serialize() for menu in self.menus],
            # "distance": self.calculate_distance(user_latitude, user_longitude)
        }

    

#  many to many menuitems to menus- dinners



#list of dining hall: name location hours, menus
# 2025-04-27
# 2025-04-28
# 2025-04-29
# 2025-04-30
# 2025-05-01
# 2025-05-02
# 2025-05-03
# 2025-05-04