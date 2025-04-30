#db.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


# Menu items of all the dining halls
# Photos of the plates
# User preferences are determined whenever you open the app
# Create accounts and login (User authentication) / Delete accounts
# figure out how to do matching. (ratings can be made thru some sorting implementation)
    #Matching system (like recommending based on ratings or preferences)

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
    passwordHash = db.Column(db.String, nullable = False) #shouldn't be primary_key, multiple users can have same password
    preferences = db.relationship("Preferences", backref="user")

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email
        }



    preferences = db.relationship("Preferences", backref="user", uselist=False)
    swipes = db.relationship("Swipe", backref="user")
    

class PlatePhotos(db.Model):
    """
    Plate uploading model (Create/Update)
    
    Users upload a photo of the plate, name of dish, last time created will be listed
    details of the plate will be provided in database

    Many to one relationship with dininghall and menu
    """
    __tablename__="plate"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    menuItemId= db.Column(db.Integer, db.ForeignKey("menu.id"), nullable = False)
    diningHallId= db.Column(db.Integer, db.ForeignKey("dininghall.id"), nullable = False)

    timeCreated = db.Column(db.DateTime, server_default= db.func.now())
    menu_item = db.relationship("Menu", backref = "plates") # many plates
    dining_hall = db.relationship("DiningHall", backref = "plates") # many plates

    photo = db.Column(db.String)

    def serialize(self):
        return {
            "id": self.id,
            "menuItemId": self.menuItemId,
            "diningHallId": self.diningHallId,
            "timeCreated": self.timeCreated.isoformat(),
            "photo": self.photo
        }


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
    photo = db.Column(db.String, db.ForeignKey("plate.photo"), nullable=True)
    preferenceTags =  db.Column(db.String)

    menu_item = db.relationship("Menu", backref="swipes")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "dininghallId": self.dininghallId,
            "description": self.description,
            "photo": self.photo,
            "preferenceTags": self.preferenceTags
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

    startinghour = db.Column(db.String)
    endinghour = db.Column(db.String)

    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
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
    
    def rank_by_proximity(self, user_latitude, user_longitude):
        """
        Rank dining halls by distance from user's location
        """
        all_dining_halls = DiningHall.query.all()
        dining_and_distance = []
        for hall in all_dining_halls:
            all_dining_halls.append({"dining_hall": hall, "distance": 
                                     hall.calculate_distance(user_latitude, user_longitude)})
        ranked = sorted(dining_and_distance, key = lambda x: x["distance"])
        return ranked
        

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
            "latitude":self.latitude,
            "longitude": self.longitude,
            "startinghour":self.startinghour,
            "endinghour": self.endinghour,
            "menu": [menu.serialize() for menu in self.menus],
            "distance": self.calculate_distance(user_latitude, user_longitude)
        }


class Preferences(db.Model): 
    """
    User preferences model
    One to one relationship
    """   
    __tablename__="preferences"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    # likedSwipes = 
    # dislikedSwipes = 
    dietPreferences = db.Column(db.String) #if null, they have no preferences
        # Vegetarian, Vegan,Halal, Kosher
    allergens = db.Column(db.String) #if null, they have no allergens

    activity_level = db.Column(db.String) #active, some wlaking, very close

    def serialize(self):
        return {
            "id": self.id,
            "userId": self.userId,
            # "likedSwipes": self.likedSwipes,
            # "dislikedSwipes": self.dislikedSwipes,
            "dietPreferences": self.dietPreferences,
            "allergens": self.allergens,
            "activity_level": self.activity_level
            # "name": self.name,
            # "location": self.location
        }
    #Preferences:
    # Vegetarian, Vegan,Halal, Kosher
    # "category": "Vegan/Vegetarian Offerings",
    # "category": "Halal",
    # "category": "Kosher Station",

    #allergies:
    #     alcohol, almonds, fish, hazelnuts, milk, pecan nut, pork, shellfish, tree nuts, wheat,
    #     coconut, egg, gluten, macadamia nuts, peanuts, pistachio, seasame, soy, walnuts,
        # no allergies



class Swipe(db.Model):
    """
    User swiping model to provide the student a dining hall 

    Many to one relationship, many swipes for one user
    """
    __tablename__="swipe"
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable = False)
    menuItemId= db.Column(db.Integer, db.ForeignKey("menu.id"), nullable = False)
    swipeBoolean = db.Column(db.Boolean, nullable=False) #right:true left:false

    preferencesId = db.Column(db.Integer, db.ForeignKey("preferences.id"), nullable=False)
    preferences = db.relationship("Preferences", backref="swipes")


#list of dining hall: name location hours, menus

# 2025-04-27
# 2025-04-28
# 2025-04-29
# 2025-04-30
# 2025-05-01
# 2025-05-02
# 2025-05-03
# 2025-05-04