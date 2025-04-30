#app.py

import json
import os
from projectdb import db, DiningHall, User, Preferences
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

db_filename = "todo.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_filename}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["PLATE_UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["PLATE_UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)
with app.app_context():
    db.create_all()

    #json file reading
    with open('eateries.json','r') as file:
        data = json.load(file)
        dining_halls=[]
        for dininghall in data["data"]["eateries"]:
            date = "2025-04-29"
            all_events=[]
            for hours in dininghall["operatingHours"]:
                    if hours["date"] == date:
                        for event in hours["events"]:
                            all_events.append((event["start"], event["end"]))
            for start,end in all_events:
                dining_hall = DiningHall(
                    name = dininghall["name"],
                    latitude = dininghall["latitude"],
                    longitude = dininghall["longitude"],
                    startinghour=start,
                    endinghour=end
                )
                db.session.add(dining_hall)
            db.session.commit()

@app.route('/api/users', methods=['GET'])
def get_users():
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return jsonify(users), 200

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing input fields"}), 400
    
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"error": "Username or email already exists"}), 400
    
    user = User(
        username=username,
        name=name,
        email=email,
        passwordHash=generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    #preferences
    preferences = Preferences(

    )

@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user= User.query.filter_by(email=email).first()
    if user is None or not check_password_hash(,password):
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify(user.serialize()),200

@app.route('/api/preferences/<int:user_id>', methods=['GET'])
def get_preferences(user_id):
    preferences = Preferences.query.filter_by(userId = user_id).first()
    if preferences is None:
        return jsonify({"error": "No preferences"}), 404
    return jsonify(preferences.serialize()),200

@app.route('/api/preferences/<int:user_id>', methods=['PUT'])
def update_preferences(user_id):
    preferences = Preferences.query.filter_by(userId=user_id).first()
    if preferences is None:
        preferences = Preferences(userId=user_id)
        db.session.add(preferences)
    
    data = request.get_json()
    preferences.dietPreferences = data.get('dietPreferences', preferences.dietPreferences)
    preferences.allergens = data.get('allergens', preferences.allergens)
    db.session.commit()

@app.route('/api/dininghalls', methods=['GET'])
def get_dining_halls():
    dining_halls = []
    for dining_hall in DiningHall.query.all():
        dining_halls.append(dining_hall.serialize())
    return jsonify(dining_halls), 200

@app.route('/api/upload', methods=['POST'])
def upload_photos():
    picture = request.files['picture']
    if picture is None:
        return jsonify({"error": "No picture"}),404
    
    plate = PlatePhotos(
        menuItemId=,
        diningHallId=,
        photo=
    )
    db.session.add(plate)

    db.session.commit()
    return jsonify(plate.serialize()),201



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
