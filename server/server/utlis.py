from ninja.security import HttpBearer
import server.secret_config as secrets
class Auth(HttpBearer):
    def authenticate(self, request, token):
        if token == secrets.auth_token:
            return True
        return False