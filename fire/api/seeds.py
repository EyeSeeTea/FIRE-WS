import json
from datetime import datetime
from sqlalchemy import inspect

from fire.api import app, models, db

def create(model_class, unique_attributes, attributes_dict):
    objects_dict = {key: model_class(**attributes) for (key, attributes) in attributes_dict.items()}
    output = {}
    for attr, obj in objects_dict.items():
        filter = {attr: getattr(obj, attr) for attr in unique_attributes}
        existing_obj = model_class.query.filter_by(**filter).first()
        if not existing_obj:
            db.session.add(obj)
        output[attr] = existing_obj or obj
    db.session.commit()
    return output

def run():
    users = create(models.User, ["username"], {
        "joel": {
            "name": "Joel Fleischman",
            "username": "joel",
            "address": "Flushing, Queens (New York City)",
            "admin": True,
            "gender": "male",
            "avatar_url" : "http://24.media.tumblr.com/tumblr_lrt2nf1G7Y1qh4q2fo4_500.png",
            "email": "joel.fleischman@mail.com",
            "state": "active",
            "phone_number": "1",
        },
        "maggie": {
            "name": "Maggie O'Connell",
            "username": "maggie",
            "address": "Cicely, Alaska",
            "admin": True,
            "gender": "female",
            "avatar_url" : "https://s-media-cache-ak0.pinimg.com/736x/ab/e9/33/abe93316032b2eb1c0f0a28d0761247d.jpg",
            "email": "maggie.oconnell@mail.com",
            "state": "active",
            "phone_number": "2",
        },
        "marilyn": {
            "name": "Marilyn Whirlwind",
            "username": "marilyn",
            "address": "Cicely, Alaska",
            "admin": False,
            "gender": "female",
            "avatar_url" : "http://www.moosechick.com/Marilyn-totem.JPG",
            "email": "marilyn.whildwind@mail.com",
            "state": "active",
            "phone_number": "3",
        },
        "chris": {
            "name": "Chris Stevens",
            "username": "chris",
            "address": "KBHR 570, Alaska",
            "admin": False,
            "gender": "male",
            "avatar_url" : "https://s-media-cache-ak0.pinimg.com/originals/95/0f/80/950f80784424912493374c60c6530a16.jpg",
            "email": "chris.stevens@mail.com",
            "state": "inactive",
        },
        "maurice": {
            "name": "Maurice Minnifield",
            "username": "maurice",
            "address": "Some Ranch Somewhere, Alaska",
            "admin": False,
            "gender": "male",
            "avatar_url" : "http://www.barrycorbin.com/maurice/stills/Barry_maurice1.jpg",
            "email": "maurice@mail.com",
            "state": "inactive",
        },
    })

    new_user_requests = create(models.NewUserRequest, ["user_id", "state"], {
        "maggie_accepted": {
            "user_id": users["maggie"].id,
            "admin_user_id": users["joel"].id,
            "state": "accepted",
        },
        "marilyn_accepted": {
            "user_id": users["marilyn"].id,
            "admin_user_id": users["joel"].id,
            "state": "accepted",
        },
        "chris_pending": {
            "user_id": users["chris"].id,
            "admin_user_id": None,
            "state": "pending",
        },
        "maurice_rejected": {
            "user_id": users["maurice"].id,
            "admin_user_id": users["joel"].id,
            "state": "rejected",
        },
    })

    messages = create(models.Message, ["from_user_id", "to_user_id", "text"], {
        "from_maggie_to_marilyn": {
            "text": "Were you able to call?",
            "from_user_id": users["maggie"].id,
            "to_user_id": users["marilyn"].id,
        },
        "from_joel_to_marilyn": {
            "text": "Make sure you have credit before making a call",
            "from_user_id": users["joel"].id,
            "to_user_id": users["marilyn"].id,
        },
    })

    vouchers = create(models.Voucher, ["user_id", "code"], {
        "joel_active": {
            "user_id": users["joel"].id,
            "state": "active",
            "credit_remaining": 40,
            "credit_total": 50,
            "code": "voucher1",
            "url": "http://vouchers/50",
            "bulk_number": "bulk-50",
            "vendor": "EstPhonic",
            "activated": datetime(2016, 7, 26, 23, 50),
            "depleted": None,
        },
        "marilyn_depleted": {
            "user_id": users["marilyn"].id,
            "state": "depleted",
            "credit_remaining": 0,
            "credit_total": 80,
            "code": "voucher2",
            "url": "http://vouchers/80",
            "bulk_number": "bulk-80",
            "vendor": "EstPhonic",
            "activated": datetime(2016, 7, 26, 23, 50),
            "depleted": datetime(2016, 7, 29, 20, 50),
        },
        "unassigned": {
            "user_id": None,
            "state": "inactive",
            "credit_remaining": 70,
            "credit_total": 70,
            "code": "voucher3",
            "url": "http://vouchers/3",
            "bulk_number": "bulk-80",
            "vendor": "EstPhonic",
            "activated": None,
            "depleted": None,
        },
    })

    notifications = create(models.Notification,
        ["type", "new_user_request_id", "message_id", "user_id", "voucher_id"], {
        "new_user_request": {
            "type": "newUserRequest",
            "new_user_request_id": new_user_requests["chris_pending"].id,
        },
        "new_user_accepted": {
            "type": "newUserAccepted",
            "new_user_request_id": new_user_requests["marilyn_accepted"].id,
        },
        "new_user_rejected": {
            "type": "newUserRejected",
            "new_user_request_id": new_user_requests["maurice_rejected"].id,
        },
        "message_sent": {
            "type": "messageSent",
            "message_id": messages["from_maggie_to_marilyn"].id,
        },
        "profile_updated": {
            "type": "profileUpdated",
            "user_id": users["maggie"].id,
        },
        "voucher_tooped_up": {
            "type": "toppedUp",
            "voucher_id": vouchers["marilyn_depleted"].id,
        },
    })

    return dict(
        users=users,
        new_user_requests=new_user_requests,
        vouchers=vouchers,
        messages=messages,
        notifications=notifications
    )
