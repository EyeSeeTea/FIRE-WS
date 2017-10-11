from datetime import datetime

from sqlalchemy.orm import relationship

from savalidation import ValidationMixin
import savalidation.validators as val

from fire.api import db

class User(db.Model, ValidationMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    address = db.Column(db.String(255))
    admin = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(80))
    avatar_url = db.Column(db.String(1024))
    state = db.Column(db.String(64))
    phone_number = db.Column(db.String(20))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_access = db.Column(db.DateTime)
    notifications = relationship("Notification")

    val.validates_constraints()
    val.validates_presence_of("name")
    val.validates_one_of('gender', ["female", "male", "unspecified"])
    val.validates_one_of('state', ["pending", "active", "inactive"])

    def __repr__(self):
        return '<User(id={id!r} name={name!r}, phone_number={phone_number!r}, state={state!r})>'.\
            format(id=self.id, name=self.name, phone_number=self.phone_number, state=self.state)

class NewUserRequest(db.Model, ValidationMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = relationship("User", foreign_keys=[user_id])
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_user = relationship("User", foreign_keys=[admin_user_id])
    created = db.Column(db.DateTime, default=datetime.utcnow)
    state = db.Column(db.String(64))

    val.validates_constraints()
    val.validates_one_of('state', ["pending", "accepted", "rejected"])

    def __repr__(self):
        return '<NewUserRequest(id={id!r}, user={user!r}, state={state!r})>'.\
            format(id=self.id, user=self.user, state=self.state)

class Message(db.Model, ValidationMixin):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user = relationship("User", foreign_keys=[to_user_id])
    created = db.Column(db.DateTime, default=datetime.utcnow)
    notifications = relationship("Notification")

    val.validates_constraints()

class Voucher(db.Model, ValidationMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User")
    state = db.Column(db.String(64))
    code = db.Column(db.String(64))
    url = db.Column(db.String(1024))
    bulk_number = db.Column(db.String(128))
    vendor = db.Column(db.String(128))
    credit_total = db.Column(db.Integer)
    credit_remaining = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    activated = db.Column(db.DateTime)
    depleted = db.Column(db.DateTime)
    notifications = relationship("Notification")

    val.validates_constraints()

class Notification(db.Model, ValidationMixin):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(64))
    new_user_request_id = db.Column(db.Integer, db.ForeignKey('new_user_request.id'))
    new_user_request = relationship("NewUserRequest")
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    message = relationship("Message", back_populates="notifications")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User", back_populates="notifications")
    voucher_id = db.Column(db.Integer, db.ForeignKey('voucher.id'))
    voucher = relationship("Voucher", back_populates="notifications")

    val.validates_constraints()
    val.validates_one_of('type',
        ["newUserRequest", "newUserAccepted", "newUserRejected", "messageSent", "profileUpdated", "toppedUp"])
