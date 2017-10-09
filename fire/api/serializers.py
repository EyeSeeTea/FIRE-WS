from marshmallow import fields
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
    user = fields.Nested(UserSchema)
    admin_user = fields.Nested(UserSchema, dump_to="adminUser")

    class Meta(BaseSchema.Meta):
        model = models.NewUserRequest

class MessageSchema(BaseSchema):
    from_user = fields.Nested(UserSchema, dump_to="fromUser")
    to_user = fields.Nested(UserSchema, dump_to="toUser")

    class Meta(BaseSchema.Meta):
        model = models.Message

class VoucherSchema(BaseSchema):
    user = fields.Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        exclude = ["notifications"]
        model = models.Voucher

class NotificationSchema(BaseSchema):
    voucher = fields.Nested(VoucherSchema)
    new_user_request = fields.Nested(NewUserRequestSchema, dump_to="newUserRequest")
    message = fields.Nested(MessageSchema)
    user = fields.Nested(UserSchema)

    class Meta(BaseSchema.Meta):
        model = models.Notification

schemas = {
    models.User: UserSchema(extra={"sip": {"host": config.get(["sip", "host"])}}),
    models.NewUserRequest: NewUserRequestSchema(),
    models.Message: MessageSchema(),
    models.Voucher: VoucherSchema(),
    models.Notification: NotificationSchema(),
}

def get_schema_for_model(model):
    return schemas[model]
