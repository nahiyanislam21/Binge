#app.py

import json
import os
from projectdb import db, DiningHall, User, Swipe, MenuItem, UserSwipeTable
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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

@app.route('/api/users', methods=['GET'])
def get_users(): #✅
    users = []
    for user in User.query.all():
        users.append(user.serialize())
    return jsonify(users), 200

@app.route('/api/users/register', methods=['POST'])
def register_user(): #✅
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
    return jsonify(user.serialize()), 201

@app.route('/api/users/login', methods=['POST'])
def login_user(): #✅
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user= User.query.filter_by(email=email).first()
    if user is None or not check_password_hash(user.passwordHash, password):
        return jsonify({"error": "Invalid username or password"}), 401
    return jsonify(user.serialize()),200

@app.route('/api/dininghalls', methods=['GET'])
def get_dining_halls(): #✅
    dining_halls = []
    for dining_hall in DiningHall.query.all():
        dining_halls.append(dining_hall.serialize())
    return jsonify(dining_halls), 200

@app.route('/api/users/<int:user_id>', methods=['DELETE']) # new method C R U D-Delete
def delete_user_account(user_id): 
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify(user), 200


# @app.route('/api/upload', methods=['POST'])
# def upload_photos():
#     picture = request.files.get['picture']
#     menu_item_id = request.form.get('menuItemId')
#     dining_hall_id = request.form.get('diningHallId')

#     if picture is None:
#         return jsonify({"error": "No picture"}),404
    
#     filename = secure_filename(picture.filename)
#     filepath = os.path.join("static/uploads", picture.filename)
#     picture.save(filepath)

#     plate = PlatePhotos(
#         menuItemId=menu_item_id,
#         diningHallId= dining_hall_id,
#         photo=picture
#     )

#     db.session.add(plate)
#     db.session.commit()
#     return jsonify(plate.serialize()),201

@app.route('/api/rank_by_distance', methods=['GET'])
def rank_by_distance(): #✅
    user_latitude = request.args.get('latitude', type=float)
    user_longitude = request.args.get('longitude', type=float)
    all_dining_halls = DiningHall.query.all()
    dining_and_distance = []
    for hall in all_dining_halls:
        dining_and_distance.append({
            "dining_hall": hall.serialize(user_latitude, user_longitude),
            "distance": hall.calculate_distance(user_latitude, user_longitude)
        })
    return jsonify(dining_and_distance), 200

@app.route('/api/swipe', methods=['POST'])
def swipe():
    """
    Swipe on a menu item
    """
    data = request.get_json()
    user_id = data.get('userId')
    menu_item_id = data.get('menuItemId')
    swipe_boolean = data.get('swipeBoolean')

    if None in [user_id, menu_item_id, swipe_boolean]:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    menu_item = MenuItem.query.get(menu_item_id)

    if not user or not menu_item:
        return jsonify({"error": "Invalid user or menu item"}), 404
        
    swipe = Swipe(
        userId=user_id,
        menuItemId=menu_item_id,
        swipeBoolean=swipe_boolean
    )
    db.session.add(swipe)

    if swipe_boolean:
        for dininghall in menu_item.dining_halls:
            dininghall.swipeCount +=1

    db.session.commit()
    return jsonify(swipe.serialize()), 201

@app.route('/api/userSwipeTable/<int:user_id>', methods=['GET'])
def get_user_swipe_table(user_id):
    """
    Get the swipe table for a user
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    swipes = UserSwipeTable.query.filter_by(userId=user_id).all()
    
    return jsonify([swipe.serialize() for swipe in swipes]), 200


@app.route('/api/dining/menu/<string:name>', methods = ['GET'])
def get_dining_hall_menu(name):
    """
    Get the menu for a dining hall
    """
    dining_hall= DiningHall.query.filter_by(name=name).first()
    if dining_hall is None:
        return jsonify({"error":"Dining hall was not found"}), 404
    menu_items = [item.name for item in dining_hall.menu_items]
    return jsonify({
        "dining_hall": name,
        "menu_items": menu_items
    }), 200


@app.route('/api/item/<string:name>', methods = ['GET'])
def get_item_dining_halls(name):
    """
    Get the dining halls an item is in
    """
    item = MenuItem.query.filter_by(name=name).first()
    if item is None:
        return jsonify({"error":"Item was not found"}), 404
    
    dining_halls = [hall.name for hall in item.dining_halls]

    return jsonify({
        "item": name,
        "menu_items": dining_halls
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

