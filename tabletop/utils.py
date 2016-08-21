from tabletop import *

twilio_client = None


# TODO: automatically merge [secret] plugin config with secret config options in global c object
def initialize_twilio():
    try:
        twilio_sid = tabletop_config['secret']['twilio_sid']
        twilio_token = tabletop_config['secret']['twilio_token']

        if twilio_sid and twilio_token:
            twilio_client = TwilioRestClient(twilio_sid, twilio_token)
        else:
            log.debug('Twilio SID and/or TOKEN is not in INI, not going to try to start Twilio for SMS messaging')
    except:
        log.error('twilio: unable to initialize twilio REST client', exc_info=True)
        twilio_client = None

on_startup(initialize_twilio, priority=49)


def normalize(phone_number):
    return phonenumbers.format_number(phonenumbers.parse(phone_number, c.PHONE_COUNTRY), PhoneNumberFormat.E164)


def send_sms(to, body, from_=c.TWILIO_NUMBER):
    to = normalize(to)
    if not twilio_client:
        log.error('no twilio client configured')
    elif c.DEV_BOX and to not in c.TEST_NUMBERS:
        log.info('We are in dev box mode, so we are not sending {!r} to {!r}', body, to)
    else:
        return twilio_client.messages.create(to=to, body=body, from_=normalize(from_))
