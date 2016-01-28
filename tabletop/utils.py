from tabletop import *

# TODO: automatically merge [secret] plugin config with secret config options in global c object
client = TwilioRestClient(tabletop_config['secret']['twilio_sid'], tabletop_config['secret']['twilio_token'])


def send_sms(to, body, _from=c.TWILIO_NUMBER):
    return client.messages.create(to=normalize(to), body=body, from_=normalize(from_))


def normalize(phone_number):
    return phonenumbers.format_number(phonenumbers.parse(phone_number, c.PHONE_COUNTRY), PhoneNumberFormat.E164)
