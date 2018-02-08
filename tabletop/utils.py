from tabletop import *

twilio_client = None
try:
    twilio_sid = tabletop_config['secret']['tabletop_twilio_sid']
    twilio_token = tabletop_config['secret']['tabletop_twilio_token']

    if twilio_sid and twilio_token:
        twilio_client = TwilioRestClient(twilio_sid, twilio_token)
    else:
        log.debug(
            'Tabletop twilio SID and/or TOKEN is not in INI, not going to try '
            'to start twilio for tabletop SMS messaging')
except Exception:
    log.error('twilio: unable to initialize twilio REST client', exc_info=True)
    twilio_client = None


def normalize(phone_number):
    return phonenumbers.format_number(
        phonenumbers.parse(phone_number, c.TABLETOP_PHONE_COUNTRY),
        PhoneNumberFormat.E164)


def send_sms(to, body, from_=c.TABLETOP_TWILIO_NUMBER):
    to = normalize(to)
    if not twilio_client:
        log.error('no twilio client configured')
    elif c.DEV_BOX and to not in c.TESTING_PHONE_NUMBERS:
        log.info(
            'We are in dev box mode, so we are not sending {!r} to {!r}',
            body, to)
    else:
        return twilio_client.messages.create(
            to=to, body=body, from_=normalize(from_))
