 #json file reading
import json
from projectdb import db, DiningHall, MenuItem, menus_table

with open('/app/eateries.json','r') as file:
    data = json.load(file)
    date = "2025-04-29"
    dining_halls=[]
    for dininghall in data["data"]["eateries"]:
        name = dininghall["name"]
        dinner_menu_items = []

        for hours in dininghall["operatingHours"]:
                if hours["date"] == date:
                     for event in hours["events"]:
                          if event.get("descr") == "Dinner":
                               for category in event["menu"]:
                                    for item in category.get("items",[]):
                                         dinner_menu_items.append(item["item"])
        if dinner_menu_items:
            dining_hall = DiningHall(
                name = name
            )
            db.session.add(dining_hall)
            db.session.flush()

            for item_name in dinner_menu_items:
                menu_item = MenuItem.query.filter_by(name=item_name).first()
                if not menu_item:
                    menu_item = MenuItem(name=item_name)
                    db.session.add(menu_item)
                    db.session.flush()

                # Insert into association table
                append = menus_table.insert().values(
                    dining_hall=dining_hall.id,
                    menu_item=menu_item.id
                )
                db.session.execute(append)
    db.session.commit()