from .user import User


class GameUser:
    """
    Represents a user inside a game; has some extra properties.
    """

    def __init__(self, user, roles):
        self._user = user
        self._roles = roles.split()
