from tabletop import *


def send_reminder(entrant):
    sid = 'unable to send sms'
    try:
        body = c.REMINDER_SMS.format(entrant=entrant)
        message = send_sms(entrant.attendee.cellphone, body)
        if message:
            sid = message.sid if not message.error_code else message.error_text
    except TwilioRestException as e:
        if e.code == 21211:  # https://www.twilio.com/docs/api/errors/21211
            log.error('invalid cellphone number for entrant', exc_info=True)
        else:
            log.error('unable to send reminder SMS', exc_info=True)
            raise
    except:
        log.error('Unexpected error sending SMS', exc_info=True)
        raise

    entrant.session.add(TabletopSmsReminder(entrant=entrant, text=body, sid=sid))
    entrant.session.commit()


def send_reminder_texts():
    if not twilio_client:
        return

    with Session() as session:
        for entrant in session.entrants():
            if entrant.should_send_reminder:
                send_reminder(entrant)


def check_replies():
    if not twilio_client:
        return

    with Session() as session:
        entrants = session.entrants_by_phone()
        existing_sids = {sid for [sid] in session.query(TabletopSmsReply.sid).all()}
        for message in twilio_client.messages.list(to=c.TWILIO_NUMBER):
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


if c.SEND_SMS:
    DaemonTask(check_replies, interval=120, name="sms_chk_replies")
    DaemonTask(send_reminder_texts, interval=120, name="sms_send_remind")
else:
    log.info('SMS DISABLED for tabletop')
