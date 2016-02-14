from tabletop import *

# TODO: automatically merge [secret] plugin config with secret config options in global c object
try:
    client = TwilioRestClient(tabletop_config['secret']['twilio_sid'], tabletop_config['secret']['twilio_token'])
except:
    log.error('unable to initialize twilio rest client; you probably need to set the sid / token', exc_info=True)
    client = None


def normalize(phone_number):
    return phonenumbers.format_number(phonenumbers.parse(phone_number, c.PHONE_COUNTRY), PhoneNumberFormat.E164)


def send_sms(to, body, from_=c.TWILIO_NUMBER):
    to = normalize(to)
    if not client:
        log.error('no twilio client configured')
    elif c.DEV_BOX and to not in c.TEST_NUMBERS:
        log.info('We are in dev box mode, so we are not sending {!r} to {!r}', body, to)
    else:
        return client.messages.create(to=to, body=body, from_=normalize(from_))
