class RoomDesc:
    """
    A room description.
    """
    def __init__(self, channel_id, description, owners):
        self._channel_id = channel_id
        self._description = description
        self._owners = owners
