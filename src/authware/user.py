import dateutil.parser
import aiohttp

from uuid import UUID

import requests

from .utils import Authware


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
        result = {"id": from_union([lambda x: str(x), from_none], self.id),
                  "name": from_union([from_str, from_none], self.name), "variables": from_union(
                [lambda x: from_list(lambda x: x, x), from_none], self.variables)}
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
        result = {"id": from_union([lambda x: str(x), from_none], self.id), "date_created": from_union(
            [lambda x: x.isoformat(), from_none], self.date_created)}
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
        result = {"id": from_union([lambda x: str(x), from_none], self.id),
                  "key": from_union([from_str, from_none], self.key),
                  "value": from_union([from_str, from_none], self.value), "can_user_edit": from_union(
                [from_bool, from_none], self.can_user_edit)}
        return result

    async def delete(self) -> dict:
        delete_payload = {
            "key": self.key
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.delete("/user/variables", json=delete_payload) as resp:
                delete_response = await Authware.check_response(resp)

        return delete_response

    async def update(self, new_value: str) -> dict:
        update_payload = {
            "key": self.key,
            "value": new_value
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.put("/user/variables", json=update_payload) as resp:
                update_response = await Authware.check_response(resp)

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
        result = {"role": from_union(
            [lambda x: to_class(Role, x), from_none], self.role),
            "username": from_union([from_str, from_none], self.username),
            "id": from_union([lambda x: str(x), from_none], self.id),
            "email": from_union([from_str, from_none], self.email), "date_created": from_union(
                [lambda x: x.isoformat(), from_none], self.date_created), "expiration": from_union(
                [lambda x: x.isoformat(), from_none], self.expiration), "sessions": from_union([lambda x: from_list(
                lambda x: to_class(Session, x), x), from_none], self.sessions), "requests": from_union(
                [lambda x: from_list(lambda x: x, x), from_none], self.requests),
            "user_variables": from_union([lambda x: from_list(
                lambda x: to_class(UserVariable, x), x), from_none], self.user_variables)}
        return result

    async def create_user_variable_async(self, key: str, value: str, can_edit: bool) -> dict:
        create_payload = {
            "key": key,
            "value": value,
            "can_user_edit": can_edit
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/user/variables", json=create_payload) as resp:
                create_response = await Authware.check_response(resp)

        return create_response

    def create_user_variable(self, key: str, value: str, can_edit: bool) -> dict:
        create_payload = {
            "key": key,
            "value": value,
            "can_user_edit": can_edit
        }

        req = requests.post(Authware.base_url + "/user/variables", json=create_payload, headers=Authware.headers)
        create_response = Authware.check_response_sync(req)

        return create_response

    async def change_email_async(self, new_email: str, password: str) -> dict:
        change_payload = {
            "new_email_address": new_email,
            "password": password
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.put("/user/change-email", json=change_payload) as resp:
                change_response = await Authware.check_response(resp)

        return change_response

    async def change_password_async(self, old_password: str, new_password: str, repeat_password: str) -> dict:
        change_payload = {
            "old_password": old_password,
            "password": new_password,
            "repeat_password": repeat_password
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.put("/user/change-password", json=change_payload) as resp:
                change_response = await Authware.check_response(resp)

        return change_response

    async def execute_api_async(self, api_id: str, params: dict) -> dict:
        execute_payload = {
            "api_id": api_id,
            "parameters": params
        }

        async with aiohttp.ClientSession(base_url=Authware.base_url, headers=Authware.headers) as session:
            async with session.post("/api/execute", json=execute_payload) as resp:
                change_response = await Authware.check_response(resp)

        return change_response

    def change_email(self, new_email: str, password: str) -> dict:
        change_payload = {
            "new_email_address": new_email,
            "password": password
        }

        req = requests.put(Authware.base_url + "/user/change-email", json=change_payload, headers=Authware.headers)
        change_response = Authware.check_response_sync(req)

        return change_response

    def change_password(self, old_password: str, new_password: str, repeat_password: str) -> dict:
        change_payload = {
            "old_password": old_password,
            "password": new_password,
            "repeat_password": repeat_password
        }

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
