from datetime import datetime

from fire.api import models, serializers, db
from fire.api import ObjectNotFound
from flask_servicelayer import SQLAlchemyService

def to_json(obj_or_objs):
    if isinstance(obj_or_objs, dict):
        return obj_or_objs
    elif isinstance(obj_or_objs, list):
        objs = obj_or_objs
        return [to_json(obj) for obj in objs]
    else:
        obj = obj_or_objs
        return serializers.get_schema_for_model(type(obj)).dump(obj).data

class CustomSQLAlchemyService(SQLAlchemyService):
    def get_or_raise(self, id):
        table_name = self.__model__.__table__.name
        return self.get(id) or self.not_found("{}[id={}]".format(table_name, id))

    def not_found(self, msg=None):
        raise ObjectNotFound(msg)

class UserService(CustomSQLAlchemyService):
    __model__ = models.User
    __db__ = db

    def get_messages(self, user):
        return models.Message.query.filter_by(to_user_id=user.id).all()

    def get_vouchers(self, user):
        return models.Voucher.query.filter_by(user_id=user.id).all()

class NewUserRequestService(CustomSQLAlchemyService):
    __model__ = models.NewUserRequest
    __db__ = db

    def create_from_request(self, attributes):
        schema = serializers.get_schema_for_model(models.NewUserRequest)
        new_user_request = schema.load(attributes).data
        new_user_request.state = "pending"
        new_user_request.user.state = "pending"
        return self.save(new_user_request)

    def accept(self, new_user_request, admin_user):
        if new_user_request.state == "pending":
            new_user_request.state = "accepted"
            new_user_request.user.state = "active"
            new_user_request.admin_user = admin_user
            return self.save(new_user_request)

    def reject(self, new_user_request, admin_user):
        if new_user_request.state == "pending":
            new_user_request.state = "rejected"
            new_user_request.admin_user = admin_user
            return self.save(new_user_request)

class NotificationService(CustomSQLAlchemyService):
    __model__ = models.Notification
    __db__ = db

    def paginated(self):
        return self.paginate(page=1, per_page=50, order_by=models.Notification.created)

class MessageService(CustomSQLAlchemyService):
    __model__ = models.Message
    __db__ = db

class VoucherService(CustomSQLAlchemyService):
    __model__ = models.Voucher
    __db__ = db

    def activate_by_code(self, user, code):
        voucher = self.first(code=code, state="inactive") \
            or self.not_found("Voucher with code {}".format(code))
        voucher.state = "active"
        voucher.activated = datetime.utcnow()
        voucher.user = user
        return self.save(voucher)

## Not persisted

pricing = {
    "local_mobile": 1.5,
    "local_land_lines": 0.8,
    "national_mobile": 2.3,
    "national_land_lines": 2.1,
    "international": [
        {
            "country": "Sierra Leone",
            "mobile": 8.4,
            "land_lines": 5.3,
        },
        {
            "country": "Rwanda",
            "mobile": 9.2,
            "land_lines": 6.3,
        },
    ]
}

call_pricing = {
    "gsm": 1.5,
    "voip": 0.01,
}
