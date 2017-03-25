class User:
    """
    A KGS user account.
    """

    FLAGS = (
        'g',  # guest
        'c',  # connected
        'd',  # account deleted
        's',  # sleeping (inactive for over 10 min)
        'a',  # user has an avatar
        'r',  # robot
        'TT',  # has won a KGS tournament (congrats, buddy!)
        't',  # runner-up in a KGS tournament (not bad, not bad)
        'p',  # currently playing a game
        'P',  # currently playing in a KGS tournament game
        '*',  # KGS Plus subscriber
        '!',  # KGS Meijin
        '=',  # Can play ranked games
        '~',  # Plays stronger players far more often that weaker ones
    )

    AUTH_LEVELS = (
        'normal',  # default
        'robot_ranked',
        'teacher',
        'jr_admin',
        'sr_admin',
        'super_admin',
    )

    def __init__(self, name, flags, rank='', auth_level='normal'):
        """
        Constructor.

        :param name: The user name
        :param flags: List of flags (see info file)
        :param rank: Rank of the user, empty means no rank.
        :param auth_level:
        """
        self._name = name
        self._rank = rank
        self._auth_level = auth_level

        # Build flags from string
        self._flags = list()
        self.build_flags(flags)

    def build_flags(self, flags_str):
        for char in flags_str:
            self.add_flag(char)

    def add_flag(self, flag):
        if flag in self.FLAGS:
            self._flags.append(flag)
        else:
            raise ValueError('Invalid flag character ' + flag)

    @property
    def auth_level(self):
        return self._auth_level

    @auth_level.setter
    def auth_level(self, auth_level):
        if auth_level in self.AUTH_LEVELS:
            self._auth_level = auth_level
        else:
            raise ValueError('Invalid auth level ' + auth_level)


class Friend(User):
    FRIEND_TYPES = (
        'buddy',
        'censored',
        'fan',
        'admin_track',
    )

    def __init__(self, friend_type, name, flags, rank='', auth_level='normal', notes=''):
        super(User).__init__(name, flags, rank, auth_level)
        self.friend_type = friend_type
        self.notes = notes
