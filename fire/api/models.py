from datetime import datetime

def user(user_id, private_fields=["password"]):
    user = users[user_id]
    return {k: v for (k, v) in user.items() if k not in private_fields}

def index_by_id(objs):
    return {obj["id"]: obj for obj in objs}

def get_next_id(resources):
    return (max(resource["id"] for resource in resources.values()) + 1 if resources else 1)

def get_public_user(user, private_fields=["password"]):
    return {k: v for (k, v) in user.items() if k not in private_fields}

def public_user(user_id):
    return get_public_user(user(user_id))

users = index_by_id([
    {
        "id": 1,
        "name": "Joel Fleischman",
        "username": "joel",
        "address": "Flushing, Queens (New York City)",
        "admin": True,
        "gender": "male",
        "avatarUrl" : "http://24.media.tumblr.com/tumblr_lrt2nf1G7Y1qh4q2fo4_500.png",
        "email": "joel.fleischman@mail.com",
        "state": "active",
        "phoneNumber": "123-123-001",
        "created": datetime(2016, 4, 20),
        "lastAccess": datetime(2016, 4, 24),
        "serverHost": "http://pbx.com/provision",
        "password": "joel1234",
    },
    {
        "id": 2,
        "name": "Maggie O'Connell",
        "username": "maggie",
        "address": "Cicely, Alaska",
        "admin": True,
        "gender": "female",
        "avatarUrl" : "https://s-media-cache-ak0.pinimg.com/736x/ab/e9/33/abe93316032b2eb1c0f0a28d0761247d.jpg",
        "email": "maggie.oconnell@mail.com",
        "state": "active",
        "phoneNumber": "123-123-002",
        "created": datetime(2016, 5, 10),
        "lastAccess": datetime(2016, 5, 14),
        "serverHost": "http://pbx.com/provision",
        "password": "maggie1234",
    },
    {
        "id": 3,
        "name": "Marilyn Whirlwind",
        "username": "marilyn",
        "address": "Cicely, Alaska",
        "admin": False,
        "gender": "female",
        "avatarUrl" : "http://www.moosechick.com/Marilyn-totem.JPG",
        "email": "marilyn.whildwind@mail.com",
        "state": "active",
        "phoneNumber": "123-123-003",
        "created": datetime(2014, 1, 2),
        "lastAccess": datetime(2016, 7, 26),
        "serverHost": "http://pbx.com/provision",
        "password": "marilyn1234",
    },
])

new_user_requests = index_by_id([
    {
        "id": 1,
        "user": {
            "name": "Chris Stevens",
            "username": "chris",
            "address": "KBHR 570, Alaska",
            "admin": False,
            "gender": "male",
            "avatarUrl" : "https://s-media-cache-ak0.pinimg.com/originals/95/0f/80/950f80784424912493374c60c6530a16.jpg",
            "email": "chris.stevens@mail.com",
            "phoneNumber": "123-123-004",
            "created": datetime(2014, 1, 6),
            "serverHost": "http://pbx.com/provision",
            "password": "chris1234",
        },
        "created": datetime(2014, 1, 2),
        "updated": datetime(2014, 1, 2),
        "adminUser": None,
        "state": "pending",
    },
    {
        "id": 2,
        "user": public_user(2),
        "created": datetime(2015, 1, 2),
        "updated": datetime(2015, 1, 2),
        "adminUser": user(1),
        "state": "accepted",
    },
])

messages = index_by_id([
    {
        "id": 1,
        "text": "Were you able to call?",
        "fromUser": public_user(1),
        "toUser": public_user(3),
        "created": datetime(2016, 7, 26, 22, 10),
    },
    {
        "id": 2,
        "text": "Make sure you have credit before making a call",
        "fromUser": public_user(1),
        "toUser": public_user(3),
        "created": datetime(2016, 7, 26, 22, 50),
    },
])

vouchers = index_by_id([
    {
        "id": 1,
        "user": public_user(1),
        "state": "active",
        "creditRemaining": 40,
        "creditTotal": 50,
        "code": "voucher1",
        "url": "http://vouchers/50",
        "bulkNumber": "bulk-50",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": datetime(2016, 7, 26, 23, 50),
        "depleted": None,
    },
    {
        "id": 2,
        "user": public_user(3),
        "state": "depleted",
        "creditRemaining": 0,
        "creditTotal": 80,
        "code": "voucher2",
        "url": "http://vouchers/80",
        "bulkNumber": "bulk-80",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": datetime(2016, 7, 26, 23, 50),
        "depleted": datetime(2016, 7, 29, 20, 50),
    },
    {
        "id": 3,
        "user": None,
        "state": "inactive",
        "creditRemaining": 70,
        "creditTotal": 70,
        "code": "voucher3",
        "url": "http://vouchers/3",
        "bulkNumber": "bulk-80",
        "Vendor": "EstPhonic",
        "created": datetime(2016, 7, 26, 22, 50),
        "activated": None,
        "depleted": None,
    },
])

notifications = index_by_id([
    {
        "id": 1,
        "type": "newUserAccepted",
        "newUserRequest": new_user_requests[2],
    },
    {
        "id": 2,
        "type": "newUserRequest",
        "newUserRequest": new_user_requests[1],
    },
    {
        "id": 3,
        "type": "messageSent",
        "message": messages[1],
    },
    {
        "id": 4,
        "type": "profileUpdated",
        "user": public_user(2),
    },
    {
        "id": 5,
        "type": "toppedUp",
        "voucher": vouchers[1],
    },
])

pricing = {
    "localMobile": 1.5,
    "localLandLines": 0.8,
    "nationalMobile": 2.3,
    "nationalLandLines": 2.1,
    "international": [
        {
            "country": "Sierra Leone",
            "mobile": 8.4,
            "landLines": 5.3,
        },
        {
            "country": "Rwanda",
            "mobile": 9.2,
            "landLines": 6.3,
        },
    ]
}

call_pricing = {
    "gsm": 1.5,
    "voip": 0.01,
}
