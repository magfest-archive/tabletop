from tabletop import *


@Session.model_mixin
class Attendee:
    games  = relationship('TabletopGame', backref='attendee')
    checkouts = relationship('TabletopCheckout', backref='attendee')
    entrants = relationship('TabletopEntrant', backref='attendee')
    sms_replies = relationship('TabletopSmsReply', backref='attendee')


@Session.model_mixin
class Event:
    tournaments = relationship('TabletopTournament', backref='event', uselist=False)


class TabletopGame(MagModel):
    code        = Column(UnicodeText)
    name        = Column(UnicodeText)
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    returned    = Column(Boolean, default=False)
    checkouts   = relationship('TabletopCheckout', backref='game')

    _repr_attr_names = ['name']

    @property
    def checked_out(self):
        try:
            return [c for c in self.checkouts if not c.returned][0]
        except:
            pass


class TabletopCheckout(MagModel):
    game_id     = Column(UUID, ForeignKey('tabletop_game.id'))
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    checked_out = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    returned    = Column(UTCDateTime, nullable=True)


class TabletopTournament(MagModel):
    event_id = Column(UUID, ForeignKey('event.id'), unique=True)
    name = Column(UnicodeText)  # might want a shorter name for SMS messages

    entrants = relationship('TabletopEntrant', backref='tournament')


class TabletopEntrant(MagModel):
    tournament_id = Column(UUID, ForeignKey('tabletop_tournament.id'))
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    signed_up = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    confirmed = Column(Boolean, default=False)

    reminder = relationship('TabletopSmsReminder', backref='entrant', uselist=False)
    replies = relationship('TabletopSmsReply', backref='entrant')

    __table_args__ = (
        UniqueConstraint('tournament_id', 'attendee_id', name='_tournament_entrant_uniq'),
    )


class TabletopSmsReminder(MagModel):
    entrant_id = Column(UUID, ForeignKey('tabletop_entrant.id'), unique=True)
    when = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    text = Column(UnicodeText)


class TabletopSmsReply(MagModel):
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    entrant_id = Column(UUID, ForeignKey('tabletop_entrant.id'), nullable=True)
    when = Column(UTCDateTime)
    text = Column(UnicodeText)
