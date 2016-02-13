from tabletop import *


def send_reminder(entrant):
    try:
        body = c.REMINDER_SMS.format(entrant=entrant)
        message = send_sms(entrant.attendee.cellphone, body)
        assert not message.error_code, '{message.error_code}: {message.error_text}'.format(message=message)
        entrant.session.add(TabletopSmsReminder(entrant=entrant, text=body, sid=message.sid))
        entrant.session.commit()
    except:
        entrant.session.rollback()
        log.error('Unable to send reminder sms', exc_info=True)


def send_reminder_texts():
    with Session() as session:
        for entrant in session.entrants():
            if entrant.should_send_reminder:
                send_reminder(entrant)

DaemonTask(send_reminder_texts, interval=60)


def check_replies():
    with Session() as session:
        entrants = session.entrants_by_phone()
        existing_sids = {sid for [sid] in session.query(TabletopSmsReply.sid).all()}
        for message in client.messages.list(to=c.TWILIO_NUMBER):
            if message.sid in existing_sids:
                break

            for entrant in entrants[message.from_]:
                if entrant.matches(message):
                    session.add(TabletopSmsReply(
                        entrant=entrant,
                        sid=message.sid,
                        text=message.body,
                        when=message.date_sent.replace(tzinfo=UTC)
                    ))
                    entrant.confirmed = 'Y' in message.body.upper()
                    session.commit()

DaemonTask(check_replies, interval=60)
