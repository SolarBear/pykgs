import json
import time
import requests

from .messages import *
import kgs


class KgsConnection:
    """
    Creates a connection to KGS.
    """

    MAX_TIME_INACTIVITY = 10

    def __init__(self, url, user):
        self._url = url
        self._user = user
        self._message_queue = list()
        self._message_callbacks = None
        self._cookies = None
        self._keep_alive = True

        self._formatter = MessageFormatter()
        self._message_factory = MessageFactory()

        self.init_sequence()

    def init_sequence(self):
        """
        Perform the initialization sequence with the servlet.

        Basically, we perform the following operations:

        * Send LOGIN message for logging in
        * Immediately receive response to confirm data is OK
        """

        login_response = self._send_message(LoginMessage('OSRBot', ''))

        self._cookies = login_response.cookies  # NOM NOM NOM
        hello_received = False

        while not hello_received:
            response = requests.get(self._url, cookies=self._cookies)
            kgs_response = KgsResponse(self._message_factory, bytes.decode(response.content))

            if response.ok:
                for message in kgs_response.messages:
                    if type(message) is HelloMessage:
                        hello_received = True

    def loop(self):
        """
        Send queued messages and receive server responses.
        :return: bool
        """

        sleep_time = 0

        # Send queued messages
        while self._has_messages_to_process():
            time.sleep(1)  # Don't hammer the server, civility is key here, folks.
            message = self._dequeue_message()

            if message is None:
                sleep_time += 1
                if sleep_time > self.MAX_TIME_INACTIVITY:
                    # Add a WAKE_UP message so don't appear as idle
                    self.queue_message(WakeUpMessage())
            else:
                sleep_time = 0
                response = self._send_message(message)
                for callback in self._message_callbacks:
                    # TODO send something less stupid than an HttpResponse
                    callback(response)

        # TODO : find some way to
        return self._keep_alive

    def _has_messages_to_process(self):
        """
        Check if there are any messages left to send.
        :return: True if any message remains in the queue.
        """
        return len(self._message_queue) > 0

    def queue_message(self, message):
        """
        Add a message to the queue.

        Messages should definitely NOT be sent directly through _send_message: the frequency by which we send messages
        should be controlled since the KGS server does not like being spammed (and who does, really?)
        """
        if message is not Message:
            raise ValueError("Not a Message")

        self._message_queue.append(message)

    def _dequeue_message(self):
        """
        Remove a message from the queue and return it.
        :return: A Message object if any messages are left in the queue; None if no message remains.
        """
        if len(self._message_queue) > 0:
            return self._message_queue.pop()

        return None

    def _is_processable(self, message):
        """
        Tells if a given message type will be processed or not. A message is "processable" if at least one callback was
        given for it.
        :param message: Message object
        :return: True if at least one callback can be performed on that message type.
        """
        return isinstance(message, Message)\
            and message.message_type in self._message_callbacks.keys()\
            and self._message_callbacks[message.message_type].count() > 0

    def add_message_callback(self, message_type, callback):
        """
        Add a callback for a given message type response.

        :param message_type: Message type (eg. HELLO, LOGIN, etc.)
        :param callback: Callable to call with the message when we get a response.
        """
        if not callable(callback):
            raise ValueError("Callback must be a callable")
        elif not isinstance(message_type, str):
            raise ValueError("Message type must be a string")
        elif message_type not in Message.supported_types:
            raise ValueError("Message type is not supported, your pull requests are welcome")

        # Message isn't processable yet, add it to the dict of messages
        if message_type not in self._message_callbacks.keys():
            self._message_callbacks[message_type] = list()

        # Add the callback for that message
        self._message_callbacks[message_type].append(callback)

    def remove_message_callback(self, message_type, callback):
        """
        Remove a callback for a given message type response.

        :param message_type: Message type (eg. HELLO, LOGIN, etc.)
        :param callback: Callable to call with the message when we get a response.
        """
        if message_type not in self._message_callbacks:
            raise ValueError("No callbacks set for message " + message_type)
        elif callback not in self._message_callbacks[message_type]:
            raise ValueError("Callback not found in " + message_type)

        lst = self._message_callbacks[message_type]
        index = lst.index(callback)
        del lst[index]

    def _get_messages(self):
        return requests.get(self._url, '')

    def _send_message(self, message):
        """
        Private method. Send a message to the server.
        :param message: PostMessage object. Send a message to the server.
        :return: HttpResponse
        """

        if message is not Message:
            raise ValueError("Not a Message object")

        # Why would you perform a callback that will not be processed?
        if not self._is_processable(message.message_type):
            return

        formatted_message = self._formatter.format_message(message)

        if message.action == 'POST':
            headers = {"content-type": "application/json;charset=UTF-8"}
            response = requests.post(self._url, json=formatted_message, headers=headers)
        elif message.action == 'GET':
            response = requests.get(self._url, formatted_message)
        else:
            raise ValueError("Invalid action for message")

        return response

    def close(self):
        """
        Close the connection properly.
        """

        self._send_message(LogoutPostMessage())
        self._keep_alive = False
        self._cookies = None


class KgsResponse:
    """
    A response from the server (or rather, the servlet). It is simply a JSON object containing an array of messages that
    will need to be parsed and made into proper Message objects.
    """

    def __init__(self, message_factory, data):
        self._messages = list()
        self._message_factory = message_factory

        self.parse_messages(data)

    @property
    def messages(self):
        return self._messages

    def parse_messages(self, data):
        for message_dict in json.loads(data)['messages']:
            self._messages.append(self.create_message(message_dict))

    def create_message(self, message_dict):
        return self._message_factory.create_message(message_dict)


# TODO : Running as standalone to test stuff, remove this ASAP
if __name__ == '__main__':
    # TODO : create setting for actual URL
    bot = kgs.types.user.User()

    connection = KgsConnection('http://localhost:8080/jsonClient/access')

    while connection.loop():
        pass

    connection.close()  # kthxbye
