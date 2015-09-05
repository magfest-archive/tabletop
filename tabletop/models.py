from tabletop import *


@Session.model_mixin
class Attendee:
    games  = relationship('Game', backref='attendee')


class Game(MagModel):
    code        = Column(UnicodeText)
    name        = Column(UnicodeText)
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    returned    = Column(Boolean, default=False)
    checkouts   = relationship('Checkout', backref='game')

    _repr_attr_names = ['name']

    @property
    def checked_out(self):
        try:
            return [c for c in self.checkouts if not c.returned][0]
        except:
            pass


class Checkout(MagModel):
    game_id     = Column(UUID, ForeignKey('game.id'))
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    checked_out = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    returned    = Column(UTCDateTime, nullable=True)
