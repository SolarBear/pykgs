from kgs.types.user import Friend, User
from kgs.types.room_desc import RoomDesc


def _list_object_properties(obj):
    """
    Utility function that returns a list of properties contained in an object.
    :param obj:
    :return:
    """
    return filter(
        lambda a:
        not a.startswith('__')
        and a not in ['_decl_class_registry', '_sa_instance_state', '_sa_class_manager', 'metadata']
        and not callable(getattr(obj, a)),
        dir(obj))


class Message:
    """
    Abstract data class for the message to be send to KGS, please subclass.
    """

    # List of support message types
    supported_types = (
        'LOGIN',
        'HELLO',
    )

    def __init__(self, message_type, action):
        """
        Constructor.
        :param message_type: Message name (eg. LOGIN, CHAT, SET_PASSWORD, etc.)
        :param action: HTTP action (GET or POST)
        """
        self.message_type = message_type
        self.action = action

    def post_load(self):
        """
        To be called when the data from the server was received. Should be used to transform JSON dictionary into useful
        objects.
        :return:
        """
        raise NotImplementedError("Please implement the post_load method")


class PostMessage(Message):
    """
    Message sent as a POST request.
    """

    def __init__(self, message_type):
        super(Message).__init__(message_type, 'POST')

    def post_load(self):
        """
        No post-load action to perform since we're posting our own data.
        """
        pass


class GetMessage(Message):
    """
    Message sent as a GET request.
    """

    def __init__(self, message_type):
        super(Message).__init__(message_type, 'GET')

    def post_load(self):
        """
        To be called when the data from the server was received. Should be used to transform JSON dictionary into useful
        objects.
        :return:
        """
        super(Message).post_load()


class LoginMessage(PostMessage):
    """
    Request for login.
    """
    def __init__(self, name, password, locale='en_US'):
        super(PostMessage).__init__('LOGIN')
        self.name = name
        self.password = password
        self.locale = locale


class HelloMessage(GetMessage):
    """
    Very first message the server sends when try connecting.
    """
    def __init__(self):
        super(GetMessage).__init__('HELLO')
        self.versionMajor = ''
        self.versionMinor = ''
        self.versionBugfix = ''
        self.jsonClientBuild = ''


class LoginSuccessMessage(GetMessage):
    """
    Login confirmation. We may now receive further messages.
    """
    def __init__(self):
        super(GetMessage).__init__('LOGIN_SUCCESS')
        self.you = None
        self.friends = list()
        # self.subscriptions = list() TODO
        self.room_category_channel_id = list()
        self.rooms = list()

    def post_load(self):
        self._load_you()
        self._load_friends()

    def _load_you(self):
        you = self.you
        self.you = User(you['name'], you['rank'], you['flags'], you['authLevel'])

    def _load_friends(self):
        friends = self.friends
        self.friends = list()

        for friend in friends:
            self.friends.append(Friend(friend['friend_type'], friend['name'], friend['rank'],
                                       friend['flags'], friend['authLevel']))

    def _load_room_categories(self):
        room_cats = self.room_category_channel_id
        self.room_category_channel_id = dict()

        for room_cat in room_cats:
            self.room_category_channel_id[room_cat['category']] = room_cat['channelId']

    def _load_rooms(self):
        rooms = self.rooms
        self.rooms = dict()

        for room in rooms:


class LoginFailedBadPasswordMessage(GetMessage):
    def __init__(self):
        super(GetMessage).__init__('LOGIN_FAILED_BAD_PASSWORD')


class LogoutPostMessage(PostMessage):
    """
    LOGOUT message. Could be a POST or GET one
    """
    def __init__(self):
        super(PostMessage).__init__('LOGOUT')

    def post_load(self):
        pass


class RoomJoinMessage(GetMessage):
    """
    Message received when you join a room - including right after login.
    """
    def __init__(self):
        super(GetMessage).__init__('ROOM_JOIN')


class WakeUpMessage(PostMessage):
    """
    Message that simply resets your idle clock, just to keep the connection alive.
    """
    def __init__(self):
        super(PostMessage).__init__('WAKE_UP')


class MessageFormatter:
    """
    Formats a message to send to the web service which acts as a gateway to KGS.
    """

    def format_message(self, message):
        props = _list_object_properties(message)

        # Strip the beginning underscore and set the actual attribute value
        return {k: message.__getattribute__(k) for k in props}


class MessageFactory:
    """
    Takes a KGS JSON message (as a Python dict) and converts it into the proper Message object. Used for GET responses.
    """

    # Mapping of 'type' value in KGS message to their related Message subclass
    TYPE_TO_CLASS = {
        'HELLO': HelloMessage,
        'LOGIN_SUCCESS': LoginSuccessMessage,
    }

    def create_message(self, data):
        """
        Transform a JSON message into the proper Message object.
        :param data:
        :return:
        """
        # Create message object from mapping above
        message = self.TYPE_TO_CLASS[data['type']]()

        # Fill object properties from the data (fields should have the exact same name)
        for prop in _list_object_properties(message):
            if prop in data:  # If the property does not exist in the object, it's because we don't care
                if prop == 'action':
                    setattr(message, prop, 'GET')
                else:
                    setattr(message, prop, data[prop])

        # Handle some special cases (eg. the 'you' field from the LOGIN_SUCCESS message is a User object)
        message.post_load()

        return message
