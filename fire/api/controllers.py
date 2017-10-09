import functools

from flask import Flask, jsonify, make_response, request, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS

from fire import config
from fire.tools import first, merge
from fire import auth as fire_auth

from fire.api import services

# JSON Responses

def success(obj_or_objs=None):
    data = ({} if obj_or_objs is None else {"data": services.to_json(obj_or_objs)})
    json = merge({"status": "success"}, data)
    return jsonify(json)

def error(status_code, message):
    return make_response(jsonify(dict(status="error", message=message)), status_code)

def abort_with_error(status_code, message):
    abort(error(status_code, message))

# Auth

auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    user = users.first(username=username)
    return (fire_auth.get_password(user.phone_number) if user else None)

@auth.error_handler
def unauthorized():
    return error(401, "Unauthorized access")

def get_current_user():
    user = users.first(username=auth.username())
    if not user:
        abort_with_error(500, "Cannot get current user")
    else:
        return user

def admin_or_user(user_id):
    current_user = get_current_user()
    return (current_user.admin or current_user.id == user_id)

def admin_required(arg=None):
    def wrapper(f):
        @functools.wraps(f)
        @auth.login_required
        def wrapped(*args, **kwargs):
            current_user = get_current_user()
            if current_user.admin:
                return f(*args, **kwargs)
            else:
                return unauthorized()
        return wrapped
    return (wrapper(arg) if callable(arg) else wrapper)

# Resources

users = services.UserService()
new_user_requests = services.NewUserRequestService()
notifications = services.NotificationService()
messages = services.MessageService()
vouchers = services.VoucherService()

class NewUserRequestList(Resource):
    @admin_required
    def get(self):
        return success(new_user_requests.all())

    def post(self):
        new_user_request = new_user_requests.create_from_request(request.get_json())
        return success(new_user_request)

class CurrentUser(Resource):
    @auth.login_required
    def get(self):
        current_user = get_current_user()
        return success(current_user)

class UserList(Resource):
    @admin_required
    def get(self):
        return success(users.all())

class User(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        #abort_with_error(405, "Cannot get user")
        user = users.get_or_raise(user_id)
        return success(user)

    @admin_required
    def delete(self, user_id):
        user = users.get_or_raise(user_id)
        users.delete(user)
        return success()

    @admin_required
    def patch(self, user_id):
        user = users.get_or_raise(user_id)
        request_user_json = request.get_json() or {}
        users.update(user, **request_user_json)
        return success(user)

class NotificationList(Resource):
    @admin_required
    def get(self):
        return success(notifications.paginated().items)

class NewUserRequestAcceptation(Resource):
    @admin_required
    def post(self, new_user_request_id):
        new_user_request = new_user_requests.get_or_raise(new_user_request_id)
        new_user_request = new_user_requests.accept(new_user_request, admin_user=get_current_user())
        if new_user_request:
            return success(new_user_request)
        else:
            return error(400, "Cannot accept newUserRequest")

class NewUserRequestRejection(Resource):
    @admin_required
    def post(self, new_user_request_id):
        new_user_request = new_user_requests.get_or_raise(new_user_request_id)
        new_user_request = new_user_requests.reject(new_user_request, admin_user=get_current_user())
        if new_user_request:
            return success(new_user_request)
        else:
            return error(400, "Cannot reject newUserRequest")

class MessageList(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = users.get_or_raise(user_id)
        return success(users.get_messages(user))

    @admin_required
    def post(self, user_id):
        user = users.get_or_raise(user_id)
        text = request.get_json().get("text")
        message = messages.create(from_user=get_current_user(), to_user=user, text=text)
        return success(message)

class CallPricing(Resource):
    @auth.login_required
    def get(self, number):
        return success(services.call_pricing)

class UserVoucherList(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = users.get_or_raise(user_id)
        return success(users.get_vouchers(user))

    @auth.login_required
    def post(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = users.get_or_raise(user_id)
        code = request.get_json().get("code")
        voucher = vouchers.activate_by_code(user, code)
        return success(voucher)

class Pricing(Resource):
    @admin_required
    def get(self):
        return success(services.pricing)

def add_routes(app):
    api = Api(app)

    ## User not logged-in

    api.add_resource(NewUserRequestList, '/newUserRequests')

    ## Admin

    ### Notifications

    api.add_resource(NotificationList, '/notifications')
    api.add_resource(NewUserRequestAcceptation, '/newUserRequests/<int:new_user_request_id>/acceptation')
    api.add_resource(NewUserRequestRejection, '/newUserRequests/<int:new_user_request_id>/rejection')

    ### Users

    api.add_resource(CurrentUser, '/currentUser')
    api.add_resource(UserList, '/users')
    api.add_resource(User, '/users/<int:user_id>')
    api.add_resource(MessageList, '/users/<int:user_id>/messages')

    ### Billing

    api.add_resource(Pricing, '/pricing')

    ### WifiCall

    api.add_resource(CallPricing, '/callPricing/<string:number>')

    ### Vouchers

    api.add_resource(UserVoucherList, '/users/<int:user_id>/vouchers')

    return api
