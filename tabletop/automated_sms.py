from http.client import BadStatusLine
from requests.exceptions import ConnectionError

from tabletop import *


def send_reminder(entrant):
    sid = 'unable to send sms'
    try:
        body = c.TABLETOP_REMINDER_SMS.format(entrant=entrant)
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
        messages = []

        # Pull all the messages down before attempting to act on them. The new
        # twilio client uses a streaming mode, so the stream might be timing
        # out while it waits for us to act on each message inside our loop.
        try:
            messages = [m for m in twilio_client.messages.list(to=c.TABLETOP_TWILIO_NUMBER)]
        except ConnectionError as ex:
            if ex.errno == 'Connection aborted.' \
                    and isinstance(ex.strerror, BadStatusLine) \
                    and ex.strerror.line == "''":
                log.warning('Twilio connection closed unexpectedly')
            else:
                raise ex

        for message in messages:
            if message.sid in existing_sids:
                continue

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
