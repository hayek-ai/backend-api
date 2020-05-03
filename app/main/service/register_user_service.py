
class RegisterUserService:
    def register_user(self, email, username, password):
        return {'email': email, 'username': username, 'password': password}
