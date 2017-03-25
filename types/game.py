from .game_rules import GameRules


class Game:
    """
    A KGS game.
    """

    GAME_TYPES = (
        'challenge',
        'demonstration',
        'review',
        'rengo_review',
        'teaching',
        'simul',
        'rengo',
        'free',
        'ranked',
        'tournament',
    )

    SCORES = (
        'UNKNOWN',
        'UNFINISHED',
        'NO_RESULT',
        'B+RESIGN',
        'W+RESIGN',
        'B+FORFEIT',
        'W+FORFEIT',
        'B+TIME',
        'W+TIME',
    )

    def __init__(self, rules, game_type, score=None):
        self._rules = rules
        self._game_type = game_type
        self._score = score

    @property
    def game_type(self):
        return self._game_type

    @game_type.setter
    def game_type(self, game_type):
        if game_type in self.GAME_TYPES:
            self._game_type = game_type
        else:
            raise ValueError('Invalid game type ' + game_type)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        if isinstance(score, float) or isinstance(score, str) and score in self.SCORES:
            self._score = score
        else:
            raise ValueError('Invalid score ' + score)