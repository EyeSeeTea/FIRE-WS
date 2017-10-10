from marshmallow.fields import Nested
from marshmallow_sqlalchemy import ModelSchema

from fire.api import db, models
from fire import config
from fire.tools import CamelModelResourceConverter

class BaseSchema(ModelSchema):
    class Meta:
        model_converter = CamelModelResourceConverter
        sqla_session = db.session

class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = models.User

class NewUserRequestSchema(BaseSchema):
    user = Nested(UserSchema)
    admin_user = Nested(UserSchema, dump_to="adminUser")

    class Meta(BaseSchema.Meta):
        model = models.NewUserRequest

class MessageSchema(BaseSchema):
    from_user = Nested(UserSchema, dump_to="fromUser")
    to_user = Nested(UserSchema, dump_to="toUser")

    class Meta(BaseSchema.Meta):
        model = models.Message

class VoucherSchema(BaseSchema):
    user = Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        exclude = ["notifications"]
        model = models.Voucher

class NotificationSchema(BaseSchema):
    new_user_request = Nested(NewUserRequestSchema, dump_to="newUserRequest")
    message = Nested(MessageSchema)
    voucher = Nested(VoucherSchema)
    user = Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        model = models.Notification

schemas = {
    models.User: UserSchema(extra={"sip": {"host": config.get(["sip", "host"])}}),
    models.NewUserRequest: NewUserRequestSchema(),
    models.Message: MessageSchema(),
    models.Voucher: VoucherSchema(),
    models.Notification: NotificationSchema(),
}

def load(model, attributes):
    schema = schemas[model]
    return schema.load(attributes).data

def dump(obj):
    schema = schemas[type(obj)]
    return schema.dump(obj).data

def to_json(obj_or_objs):
    if isinstance(obj_or_objs, dict):
        dict_obj = obj_or_objs
        return dict_obj
    elif isinstance(obj_or_objs, list):
        objs = obj_or_objs
        return [to_json(obj) for obj in objs]
    else:
        obj = obj_or_objs
        return dump(obj)
