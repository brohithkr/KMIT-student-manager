from ninja.security import HttpBearer
import environ

env = environ.Env()
environ.Env.read_env()


class Auth(HttpBearer):
    def authenticate(self, request, token):
        if token == env("AUTH_TOKEN"):
            return True
        return False
