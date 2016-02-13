from tabletop import *

# TODO: automatically merge [secret] plugin config with secret config options in global c object
client = TwilioRestClient(tabletop_config['secret']['twilio_sid'], tabletop_config['secret']['twilio_token'])


def normalize(phone_number):
    return phonenumbers.format_number(phonenumbers.parse(phone_number, c.PHONE_COUNTRY), PhoneNumberFormat.E164)


def send_sms(to, body, from_=c.TWILIO_NUMBER):
    to = normalize(to)
    if not c.DEV_BOX or to in c.TEST_NUMBERS:
        return client.messages.create(to=to, body=body, from_=normalize(from_))
    else:
        log.info('We are in dev box mode, so we are not sending {!r} to {!r}', body, to)
