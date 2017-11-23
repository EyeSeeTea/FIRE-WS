import unittest
import json
import collections
import os
import importlib
from pprint import pprint
from datetime import datetime
from base64 import b64encode

root_dir = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(root_dir, "../../fire-ws.test.conf")
os.environ["CONFIG_FILE"] = config_path

from fire.api import server, db, seeds

class TestFireApiServer(unittest.TestCase):
    Response = collections.namedtuple("Response", ["status", "body"])

    def setUp(self):
        db.create_all()
        self.seeds = seeds.run()
        self.app = server.app
        self.app.config['TESTING'] = True
        self.client = server.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def request(self, method, path, data=None, user=None):
        kwargs1 = ({"data": json.dumps(data), "content_type": 'application/json'} if data else {})
        if user:
            username = user
            password = "pass"
            encoded_password = b64encode(bytes(username + ':' + password, "utf-8"))
            kwargs2 = {"headers": {'Authorization': 'Basic ' + encoded_password.decode("ascii")}}
        else:
            kwargs2 = {}
        kwargs = dict(kwargs1, **kwargs2)
        stream_response = getattr(self.client, method.lower())(path, **kwargs)
        status = stream_response.status_code
        body = json.loads(stream_response.get_data(stream_response))
        return self.Response(status, body)

    ### General JSON structure

    def test_existing_resource(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["marilyn"].id), user="marilyn")
        self.assertEqual(res.status, 200, res)
        self.assertEqual(res.body.get("status"), "success")
        self.assertTrue(res.body.get("data"))

    def test_not_found(self):
        res = self.request("GET", '/thisEndPointDoesNotExist')
        self.assertEqual(res.status, 404)
        self.assertEqual(res.body.get("status"), "error")
        self.assertEqual(res.body.get("message"), "The requested URL was not found on the server")

    def test_unauthorized_access(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["joel"].id))
        self.assertEqual(res.status, 401)
        self.assertEqual(res.body.get("status"), "error")
        self.assertEqual(res.body.get("message"), "Unauthorized access")

    ### Notifications

    def test_get_notifications_as_admin(self):
        res = self.request("GET", '/notifications', user="joel")
        self.assertEqual(res.status, 200, res)
        notifications = res.body["data"]
        self.assertEqual(len(notifications), 6)

    ### New User Requests

    def test_get_new_user_requests_as_admin(self):
        res = self.request("GET", '/newUserRequests', user="joel")
        self.assertEqual(res.status, 200, res)
        new_user_requests = res.body["data"]
        self.assertEqual(len(new_user_requests), 4)

    def test_get_new_user_requests_as_non_admin(self):
        res = self.request("GET", '/newUserRequests', user="marilyn")
        self.assertEqual(res.status, 401)

    def test_get_new_user_requests_unlogged(self):
        res = self.request("GET", '/newUserRequests')
        self.assertEqual(res.status, 401)

    def test_post_new_user_requests(self):
        new_user = {
            "name": "Ed Chigliak",
            "address": "Cicely, Alaska",
            "gender": "male",
            "avatarUrl" : "http://24.media.tumblr.com/tumblr_lrt2nf1G7Y1qh4q2fo4_500.png",
            "email": "ed.chigliak@mail.com",
        }
        res = self.request("POST", '/newUserRequests', {"user": new_user})
        self.assertEqual(res.status, 200, res)
        new_user_request = res.body["data"]
        self.assertTrue("adminUser" in new_user_request)
        self.assertIsNone(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["state"], "pending")
        self.assertEqual(new_user_request.get("user").get("state"), "pending")
        response_user = {k: v for (k, v) in new_user_request["user"].items() if k in new_user}
        self.assertEqual(response_user, new_user)

    def test_post_new_user_request_acceptation_activates_user(self):
        res = self.request("POST",
            '/newUserRequests/{}/acceptation'.format(self.seeds["new_user_requests"]["chris_pending"].id),
            user="joel")
        self.assertEqual(res.status, 200, res)
        new_user_request = res.body["data"]
        self.assertTrue(new_user_request)
        self.assertTrue(new_user_request.get("id"))
        self.assertEqual(new_user_request["state"], "accepted")
        self.assertTrue(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["adminUser"]["id"], self.seeds["users"]["joel"].id)
        self.assertTrue(new_user_request.get("user"))
        accepted_user = new_user_request.get("user")
        self.assertTrue(accepted_user.get("id"))

        res = self.request("GET", '/users/{}'.format(accepted_user["id"]), user=accepted_user["username"])
        self.assertEqual(res.status, 200, res)
        user = res.body["data"]
        self.assertEqual(user["state"], "active")

    def test_post_new_user_requests_acceptation_on_already_rejected_request_fails(self):
        res = self.request("POST",
            '/newUserRequests/{}/acceptation'.format(self.seeds["new_user_requests"]["maurice_rejected"].id),
            user="joel")
        self.assertEqual(res.status, 400)

    def test_post_new_user_requests_rejection_rejects_the_user(self):
        res = self.request("POST",
            '/newUserRequests/{}/rejection'.format(self.seeds["new_user_requests"]["chris_pending"].id),
            user="joel")
        self.assertEqual(res.status, 200, res)
        new_user_request = res.body["data"]
        self.assertTrue(new_user_request)
        self.assertTrue(new_user_request["id"])
        self.assertEqual(new_user_request["state"], "rejected")
        self.assertTrue(new_user_request.get("adminUser"))
        self.assertEqual(new_user_request["adminUser"]["id"], self.seeds["users"]["joel"].id)
        self.assertTrue(new_user_request.get("user"))

    def test_post_new_user_requests_rejection_on_already_accepted_request_fails(self):
        res = self.request("POST",
            '/newUserRequests/{}/rejection'.format(self.seeds["new_user_requests"]["maggie_accepted"].id),
            user="joel")
        self.assertEqual(res.status, 400)

    # Users

    def test_get_current_user_succeeds(self):
        res = self.request("GET", '/currentUser', user="marilyn")
        self.assertEqual(res.status, 200, res)
        users = res.body["data"]
        self.assertEqual(users["username"], "marilyn")

    def test_get_current_user_with_non_active_user_fails(self):
        res = self.request("GET", '/currentUser', user="chris")
        self.assertEqual(res.status, 401, res)

    def test_get_current_user_without_auth_is_not_authorized(self):
        res = self.request("GET", '/currentUser')
        self.assertEqual(res.status, 401)

    def test_get_users_as_admin_succeeds(self):
        res = self.request("GET", '/users', user="joel")
        self.assertEqual(res.status, 200, res)
        users = res.body["data"]
        self.assertEqual(len(users), 5)

    def test_get_users_as_non_admin_is_not_authorized(self):
        res = self.request("GET", '/users', user="marilyn")
        self.assertEqual(res.status, 401)

    def test_get_non_existing_user_returns_404(self):
        res = self.request("GET", '/users/123', user="joel")
        self.assertEqual(res.status, 404)

    def test_get_own_user_as_admin_succeeds(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["joel"].id), user="joel")
        self.assertEqual(res.status, 200, res)

    def test_get_other_user_as_admin_succeeds(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["maggie"].id), user="joel")
        self.assertEqual(res.status, 200, res)

    def test_get_own_user_as_user_succeeds(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["marilyn"].id), user="marilyn")
        self.assertEqual(res.status, 200, res)

    def test_get_other_user_as_user_is_not_authorized(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["joel"].id), user="marilyn")
        self.assertEqual(res.status, 401)

    def test_patch_user(self):
        data = {"email": "newemail1@mail.com"}
        res = self.request("PATCH", '/users/{}'.format(self.seeds["users"]["joel"].id), data=data, user="joel")
        self.assertEqual(res.status, 200, res)
        user = res.body["data"]
        self.assertEqual(user["email"], "newemail1@mail.com")

    def test_delete_user(self):
        res = self.request('DELETE',
            '/users/{}'.format(self.seeds["users"]["maggie"].id),
            user="joel")
        self.assertEqual(res.status, 200, res)

        res = self.request('GET',
            '/users/{}'.format(self.seeds["users"]["maggie"].id),
            user="joel")
        self.assertEqual(res.status, 404)

    def test_get_user_contains_sip_server_info(self):
        res = self.request("GET", '/users/{}'.format(self.seeds["users"]["marilyn"].id), user="marilyn")
        self.assertEqual(res.status, 200, res)
        user = res.body["data"]
        self.assertTrue(user.get("sip"))
        self.assertEqual(user.get("sip").get("host"), "localhost:5060")

    # Messages

    def test_get_user_messages_as_admin(self):
        user_id = self.seeds["users"]["marilyn"].id
        res = self.request("GET", '/users/{}/messages'.format(self.seeds["users"]["marilyn"].id), user="joel")
        self.assertEqual(res.status, 200, res)
        messages = res.body["data"]
        self.assertEqual(len(messages), 2)
        self.assertTrue(all(message["toUser"]["id"] == user_id for message in messages))

    def test_get_user_messages_as_recipient(self):
        user_id = self.seeds["users"]["marilyn"].id
        res = self.request("GET", '/users/{}/messages'.format(self.seeds["users"]["marilyn"].id), user="marilyn")
        self.assertEqual(res.status, 200, res)
        messages = res.body["data"]
        self.assertEqual(len(messages), 2)
        self.assertTrue(all(message["toUser"]["id"] == user_id for message in messages))

    def test_get_user_messages_as_normal_user_to_another_user(self):
        res = self.request("GET", '/users/{}/messages'.format(self.seeds["users"]["joel"].id), user="marilyn")
        self.assertEqual(res.status, 401)

    def test_post_user_message(self):
        user = self.seeds["users"]["marilyn"]
        post_message = {"text": "Hello there!"}
        res = self.request("POST", '/users/{}/messages'.format(user.id), data=post_message, user="joel")
        message = res.body["data"]
        self.assertEqual(res.status, 200, res)
        self.assertEqual(message["text"], "Hello there!")
        self.assertEqual(message["fromUser"].get("id"), 1)
        self.assertEqual(message["toUser"].get("id"), 3)

    # Pricing

    def test_get_pricing(self):
        res = self.request("GET", '/pricing', user="joel")
        self.assertEqual(res.status, 200, res)

    # Call Pricing

    def test_get_call_pricing(self):
        res = self.request("GET", '/callPricing/123-123-123', user="joel")
        self.assertEqual(res.status, 200, res)
        pricing = res.body["data"]
        self.assertEqual(pricing["gsm"], 1.5)
        self.assertEqual(pricing["voip"], 0.01)

    # Vouchers

    def test_get_user_vouchers(self):
        url = '/users/{}/vouchers'.format(self.seeds["users"]["marilyn"].id)
        res = self.request("GET", url, user="marilyn")
        self.assertEqual(res.status, 200, res)
        vouchers = res.body["data"]
        self.assertEqual(len(vouchers), 1)
        voucher = vouchers[0]
        self.assertTrue(voucher["user"]["id"] == 3, "bad user id")

    def test_post_user_voucher_with_code_of_inactive(self):
        user = self.seeds["users"]["marilyn"]
        post_voucher = {"code": "voucher3"}
        res = self.request("POST", '/users/{}/vouchers'.format(user.id),
                           data=post_voucher, user="marilyn")
        self.assertEqual(res.status, 200, res)
        voucher = res.body["data"]
        self.assertTrue(voucher["user"])
        self.assertEqual(voucher["user"]["id"], user.id)
        self.assertEqual(voucher["state"], "active")

    def test_post_user_voucher_with_code_of_already_active(self):
        user = self.seeds["users"]["marilyn"]
        post_voucher = {"code": "voucher1"}
        res = self.request("POST", '/users/{}/vouchers'.format(user.id), data=post_voucher, user="marilyn")
        self.assertEqual(res.status, 404)


if __name__ == "__main__":
    unittest.main()
