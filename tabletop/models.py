from tabletop import *


@Session.model_mixin
class SessionMixin:
    def entrants(self):
        return (self.query(TabletopEntrant)
                    .options(joinedload(TabletopEntrant.reminder),
                            joinedload(TabletopEntrant.attendee),
                            subqueryload(TabletopEntrant.tournament).subqueryload(TabletopTournament.event)))

    def entrants_by_phone(self):
        entrants = defaultdict(list)
        for entrant in self.entrants():
            entrants[normalize(entrant.attendee.cellphone)].append(entrant)
        return entrants


@Session.model_mixin
class Attendee:
    games  = relationship('TabletopGame', backref='attendee')
    checkouts = relationship('TabletopCheckout', backref='attendee')
    entrants = relationship('TabletopEntrant', backref='attendee')


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
    name = Column(UnicodeText)  # separate from the event name for cases where we want a shorter name in our SMS messages

    entrants = relationship('TabletopEntrant', backref='tournament')


class TabletopEntrant(MagModel):
    tournament_id = Column(UUID, ForeignKey('tabletop_tournament.id'))
    attendee_id = Column(UUID, ForeignKey('attendee.id'))
    signed_up = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    confirmed = Column(Boolean, default=False)

    reminder = relationship('TabletopSmsReminder', backref='entrant', uselist=False)
    replies = relationship('TabletopSmsReply', backref='entrant')

    @presave_adjustment
    def _within_cutoff(self):
        if self.is_new:
            tournament = self.tournament or self.session.tabletop_tournament(self.tournament_id)
            if self.signed_up > tournament.event.start_time - timedelta(minutes=c.SMS_CUTOFF_MINUTES):
                self.confirmed = True

    @property
    def should_send_reminder(self):
        return not self.confirmed and not self.reminder \
           and localized_now() < self.tournament.event.start_time \
           and localized_now() > self.signed_up + timedelta(minutes=c.SMS_STAGGER_MINUTES) \
           and localized_now() > self.tournament.event.start_time - timedelta(minutes=c.SMS_REMINDER_MINUTES)

    def matches(self, message):
        sent = message.date_sent.replace(tzinfo=UTC)
        return normalize(self.attendee.cellphone) == message.from_ \
           and self.reminder and sent > self.reminder.when \
           and sent < self.tournament.event.start_time + timedelta(minutes=c.TOURNAMENT_SLACK)

    __table_args__ = (
        UniqueConstraint('tournament_id', 'attendee_id', name='_tournament_entrant_uniq'),
    )


class TabletopSmsReminder(MagModel):
    entrant_id = Column(UUID, ForeignKey('tabletop_entrant.id'), unique=True)
    sid = Column(UnicodeText)
    when = Column(UTCDateTime, default=lambda: datetime.now(UTC))
    text = Column(UnicodeText)


class TabletopSmsReply(MagModel):
    entrant_id = Column(UUID, ForeignKey('tabletop_entrant.id'), nullable=True)
    sid = Column(UnicodeText)
    when = Column(UTCDateTime)
    text = Column(UnicodeText)
