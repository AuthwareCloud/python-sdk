import dateutil.parser
import requests

from uuid import UUID
from authware.utils import Authware


def from_none(x):
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def from_str(x):
    assert isinstance(x, str)
    return x


def from_list(f, x):
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_datetime(x):
    return dateutil.parser.parse(x)


def from_bool(x):
    assert isinstance(x, bool)
    return x


def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()


class Role:
    def __init__(self, id, name, variables):
        self.id = id
        self.name = name
        self.variables = variables

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = from_union([lambda x: UUID(x), from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))
        variables = from_union([lambda x: from_list(
            lambda x: x, x), from_none], obj.get("variables"))
        return Role(id, name, variables)

    def to_dict(self):
        result = {}
        result["id"] = from_union([lambda x: str(x), from_none], self.id)
        result["name"] = from_union([from_str, from_none], self.name)
        result["variables"] = from_union(
            [lambda x: from_list(lambda x: x, x), from_none], self.variables)
        return result


class Session:
    def __init__(self, id, date_created):
        self.id = id
        self.date_created = date_created

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = from_union([lambda x: UUID(x), from_none], obj.get("id"))
        date_created = from_union(
            [from_datetime, from_none], obj.get("date_created"))
        return Session(id, date_created)

    def to_dict(self):
        result = {}
        result["id"] = from_union([lambda x: str(x), from_none], self.id)
        result["date_created"] = from_union(
            [lambda x: x.isoformat(), from_none], self.date_created)
        return result


class UserVariable:
    def __init__(self, id, key, value, can_user_edit):
        self.id = id
        self.key = key
        self.value = value
        self.can_user_edit = can_user_edit

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        id = from_union([lambda x: UUID(x), from_none], obj.get("id"))
        key = from_union([from_str, from_none], obj.get("key"))
        value = from_union([from_str, from_none], obj.get("value"))
        can_user_edit = from_union(
            [from_bool, from_none], obj.get("can_user_edit"))
        return UserVariable(id, key, value, can_user_edit)

    def to_dict(self):
        result = {}
        result["id"] = from_union([lambda x: str(x), from_none], self.id)
        result["key"] = from_union([from_str, from_none], self.key)
        result["value"] = from_union([from_str, from_none], self.value)
        result["can_user_edit"] = from_union(
            [from_bool, from_none], self.can_user_edit)
        return result

    def delete(self) -> dict:
        delete_payload = {
            "key": self.key
        }

        delete_response = None

        req = requests.delete(Authware.base_url + "/user/variables", json=delete_payload, headers=Authware.headers)
        delete_response = Authware.check_response_sync(req)

        return delete_response

    def update(self, newValue: str) -> dict:
        update_payload = {
            "key": self.key,
            "value": newValue
        }

        update_response = None

        req = requests.put(Authware.base_url + "/user/variables", json=update_payload, headers=Authware.headers)
        update_response = Authware.check_response_sync(req)

        return update_response


class User:
    def __init__(self, role, username, id, email, date_created, expiration, sessions, requests, user_variables):
        self.role = role
        self.username = username
        self.id = id
        self.email = email
        self.date_created = date_created
        self.expiration = expiration
        self.sessions = sessions
        self.requests = requests
        self.user_variables = user_variables

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        role = from_union([Role.from_dict, from_none], obj.get("role"))
        username = from_union([from_str, from_none], obj.get("username"))
        id = from_union([lambda x: UUID(x), from_none], obj.get("id"))
        email = from_union([from_str, from_none], obj.get("email"))
        date_created = from_union(
            [from_datetime, from_none], obj.get("date_created"))
        expiration = from_union(
            [from_datetime, from_none], obj.get("expiration"))
        sessions = from_union([lambda x: from_list(
            Session.from_dict, x), from_none], obj.get("sessions"))
        requests = from_union([lambda x: from_list(
            lambda x: x, x), from_none], obj.get("requests"))
        user_variables = from_union([lambda x: from_list(
            UserVariable.from_dict, x), from_none], obj.get("user_variables"))
        return User(role, username, id, email, date_created, expiration, sessions, requests, user_variables)

    def to_dict(self):
        result = {}
        result["role"] = from_union(
            [lambda x: to_class(Role, x), from_none], self.role)
        result["username"] = from_union([from_str, from_none], self.username)
        result["id"] = from_union([lambda x: str(x), from_none], self.id)
        result["email"] = from_union([from_str, from_none], self.email)
        result["date_created"] = from_union(
            [lambda x: x.isoformat(), from_none], self.date_created)
        result["expiration"] = from_union(
            [lambda x: x.isoformat(), from_none], self.expiration)
        result["sessions"] = from_union([lambda x: from_list(
            lambda x: to_class(Session, x), x), from_none], self.sessions)
        result["requests"] = from_union(
            [lambda x: from_list(lambda x: x, x), from_none], self.requests)
        result["user_variables"] = from_union([lambda x: from_list(
            lambda x: to_class(UserVariable, x), x), from_none], self.user_variables)
        return result

    def create_user_variable(self, key: str, value: str, can_edit: bool) -> dict:
        create_payload = {
            "key": key,
            "value": value,
            "can_user_edit": can_edit
        }

        create_response = None

        req = requests.post(Authware.base_url + "/user/variables", json=create_payload, headers=Authware.headers)
        create_response = Authware.check_response_sync(req)

        return create_response

    def change_email(self, new_email: str, password: str) -> dict:
        change_payload = {
            "new_email_address": new_email,
            "password": password
        }

        change_response = None

        req = requests.put(Authware.base_url + "/user/change-email", json=change_payload, headers=Authware.headers)
        change_response = Authware.check_response_sync(req)

        return change_response

    def change_password(self, old_password: str, new_password: str, repeat_password: str) -> dict:
        change_payload = {
            "old_password": old_password,
            "password": new_password,
            "repeat_password": repeat_password
        }

        change_response = None

        req = requests.put(Authware.base_url + "/user/change-password", json=change_payload, headers=Authware.headers)
        change_response = Authware.check_response_sync(req)

        return change_response

    def execute_api(self, api_id: str, params: dict) -> dict:
        execute_payload = {
            "api_id": api_id,
            "parameters": params
        }

        req = requests.post(Authware.base_url + "/api/execute", json=execute_payload, headers=Authware.headers)
        change_response = Authware.check_response_sync(req)

        return change_response


def user_from_dict(s):
    return User.from_dict(s)


def user_to_dict(x):
    return to_class(User, x)
