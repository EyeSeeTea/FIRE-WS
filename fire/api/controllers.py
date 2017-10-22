"""
In charge of authorizations, converting from/to json and basically only the
web-facing interface.
"""

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
    user = users.get_active_user(username=username)
    return (fire_auth.get_password(user.phone_number) if user else None)


@auth.error_handler
def unauthorized():
    return error(401, "Unauthorized access")


def get_current_user():
    user = users.get_active_user(username=auth.username())
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
        return success(get_current_user())


class UserList(Resource):
    @admin_required
    def get(self):
        return success(users.all())


class User(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        # abort_with_error(405, "Cannot get user")
        return success(users[user_id])

    @admin_required
    def delete(self, user_id):
        users.delete(users[user_id])
        return success()

    @admin_required
    def patch(self, user_id):
        user = users[user_id]
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
        existing_new_user_request = new_user_requests[new_user_request_id]
        new_user_request = new_user_requests.accept(existing_new_user_request,
                                                    admin_user=get_current_user())
        if new_user_request:
            return success(new_user_request)
        else:
            return error(400, "Cannot accept newUserRequest")


class NewUserRequestRejection(Resource):
    @admin_required
    def post(self, new_user_request_id):
        existing_new_user_request = new_user_requests[new_user_request_id]
        new_user_request = new_user_requests.reject(existing_new_user_request,
                                                    admin_user=get_current_user())
        if new_user_request:
            return success(new_user_request)
        else:
            return error(400, "Cannot reject newUserRequest")


class MessageList(Resource):
    @auth.login_required
    def get(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        return success(users.get_messages(users[user_id]))

    @admin_required
    def post(self, user_id):
        text = request.get_json().get("text")
        message = messages.create(from_user=get_current_user(),
                                  to_user=users[user_id], text=text)
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
        user = users[user_id]
        return success(users.get_vouchers(user))

    @auth.login_required
    def post(self, user_id):
        if not admin_or_user(user_id):
            return unauthorized()
        user = users[user_id]
        code = request.get_json().get("code")
        voucher = vouchers.activate_by_code(user, code)
        return success(voucher)


class Pricing(Resource):
    @admin_required
    def get(self):
        return success(services.pricing)


def add_routes(app):
    api = Api(app)
    add = api.add_resource  # shortcut

    # User not logged-in

    add(NewUserRequestList, '/newUserRequests')

    # Admin

    # * Notifications

    add(NotificationList, '/notifications')
    add(NewUserRequestAcceptation, '/newUserRequests/<int:new_user_request_id>/acceptation')
    add(NewUserRequestRejection, '/newUserRequests/<int:new_user_request_id>/rejection')

    # * Users

    add(CurrentUser, '/currentUser')
    add(UserList, '/users')
    add(User, '/users/<int:user_id>')
    add(MessageList, '/users/<int:user_id>/messages')

    # * Billing

    add(Pricing, '/pricing')

    # * WifiCall

    add(CallPricing, '/callPricing/<string:number>')

    # * Vouchers

    add(UserVoucherList, '/users/<int:user_id>/vouchers')

    return api
