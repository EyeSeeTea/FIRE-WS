from datetime import datetime

from fire.api import models, serializers, db
from fire.api import ObjectNotFound
from flask_servicelayer import SQLAlchemyService

to_json = serializers.to_json

class CustomSQLAlchemyService(SQLAlchemyService):
    __db__ = db

    def not_found(self, msg=None):
        raise ObjectNotFound(msg)

    def get_or_raise(self, id):
        table_name = self.__model__.__table__.name
        return self.get(id) or self.not_found("{}[id={}]".format(table_name, id))

class UserService(CustomSQLAlchemyService):
    __model__ = models.User

    def get_active_user(self, **kwargs):
        return models.User.query.filter(models.User.state == "active").filter_by(**kwargs).first()

    def get_messages(self, user):
        return models.Message.query.filter_by(to_user=user).all()

    def get_vouchers(self, user):
        return models.Voucher.query.filter_by(user=user).all()

class NewUserRequestService(CustomSQLAlchemyService):
    __model__ = models.NewUserRequest

    def create_from_request(self, attributes):
        new_user_request = serializers.load(models.NewUserRequest, attributes)
        new_user_request.state = "pending"
        new_user_request.user.state = "pending"
        return self.save(new_user_request)

    def accept(self, new_user_request, admin_user):
        if new_user_request.state == "accepted":
            return new_user_request
        elif new_user_request.state == "pending":
            new_user_request.state = "accepted"
            new_user_request.user.state = "active"
            new_user_request.admin_user = admin_user
            return self.save(new_user_request)
        else:
            return None

    def reject(self, new_user_request, admin_user):
        if new_user_request.state == "rejected":
            return new_user_request
        elif new_user_request.state == "pending":
            new_user_request.state = "rejected"
            new_user_request.admin_user = admin_user
            return self.save(new_user_request)
        else:
            return None

class NotificationService(CustomSQLAlchemyService):
    __model__ = models.Notification

    def paginated(self):
        return self.paginate(page=1, per_page=50, order_by=models.Notification.created)

class MessageService(CustomSQLAlchemyService):
    __model__ = models.Message

class VoucherService(CustomSQLAlchemyService):
    __model__ = models.Voucher

    def activate_by_code(self, user, code):
        voucher = self.first(code=code, state="inactive") \
            or self.not_found("Voucher with code {}".format(code))
        return self.update(voucher, state="active", activated=datetime.utcnow(), user=user)

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
