from tabletop import *


@all_renderable(c.CHECKINS)
class Root:
    def index(self, session):
        return {'state': _state(session)}

    @ajax
    def create_tournament(self, session, name, event_id):
        try:
            session.add(TabletopTournament(name=name, event_id=event_id))
            session.commit()
        except:
            session.rollback()
            return {'error': 'That tournament already exists'}
        else:
            return {
                'message': 'Tournament Created',
                'state': _state(session)
            }

    @ajax
    def sign_up(self, session, tournament_id, attendee_id, cellphone):
        from uber import model_checks as umc
        if umc._invalid_phone_number(cellphone):
            return {'error': 'That is not a valid phone number'}
        try:
            attendee = session.attendee(attendee_id)
            attendee.cellphone = cellphone
            session.add(TabletopEntrant(attendee_id=attendee_id, tournament_id=tournament_id))
            session.commit()
        except:
            session.rollback()
            return {'error': 'That attendee is already signed up for that tournament'}
        else:
            return {
                'message': 'Attendee signed up',
                'state': _state(session)
            }


def _state(session):
    return {
        'events': _events(session),
        'attendees': _attendees(session),
        'tournaments': _tournaments(session),
    }


def _events(session):
    return [{
        'id': e.id,
        'name': e.name,
        'when': e.start_time_local.strftime('%-I:%M %p %A')
    } for e in session.query(Event)
                      .filter(Event.location.in_(c.TABLETOP_LOCATIONS))
                      .order_by('start_time').all()]


def _attendees(session):
    return [{
        'id': id,
        'name': name,
        'badge': num,
        'cellphone': cellphone
    } for (id, name, num, cellphone) in session.query(Attendee.id, Attendee.full_name, Attendee.badge_num, Attendee.cellphone)
                                    .filter(Attendee.badge_num != 0)
                                    .order_by(Attendee.badge_num).all()]


def _tournaments(session):
    return [{
        'id': t.id,
        'name': t.name,
        'when': t.event.start_time_local.strftime('%-I:%M %p %A'),
        'entrants': [{
            'id': te.attendee_id,
            'name': te.attendee.full_name,
            'badge': te.attendee.badge_num,
            'confirmed': te.confirmed
        } for te in t.entrants]
    } for t in session.query(TabletopTournament)
                      .options(joinedload(TabletopTournament.event),
                               subqueryload(TabletopTournament.entrants).subqueryload(TabletopEntrant.attendee))
                      .order_by('start_time').all()]
