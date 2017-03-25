class GameRules:
    """
    The set of rules used in a Game.
    """

    def __init__(self, size, rules, time_system, main_time, komi=0.0):
        """

        :param size: size of the board
        :param rules: rule set used (eg. japanese)
        :param time_system: time system used (eg. byo_yomi)
        :param main_time:
        :param komi:
        """
        self._size = size
        self._rules = rules
        self._komi = komi
        self._time_system = time_system
        self._main_time = main_time
