# Optional: You can skip this if using MySQL directly in routes
class User:
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
