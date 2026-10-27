# Lab 4A. Task 10 - Three thousand test SMS
# Student: Javohir Gayratov
#
# 10.1 Question: Name the relationship between ReminderService and SmsClient today (slide 26).
#     Why is it the wrong choice here? Think about lifetime and coupling.
#     Answer: It is composition: ReminderService creates its own SmsClient in __init__, and the
#     client lives and dies with the service. This is wrong here, because the SMS client is an
#     outside resource with its own settings. The service is tied to one concrete class and one
#     production key, and nobody (a test, staging) can give it another client.
#
# 10.2 Question: Change the design so that the SMS client is given to ReminderService from
#     outside. Where is the real SmsClient created now?
#     Answer: The client is now passed into the constructor, so the relationship is an
#     association. The real SmsClient is created once at start-up in main(), and the key is
#     read from the SMS_API_KEY environment variable.
#
# 10.3 Question: Write a FakeSmsClient that only records the messages in a list, and a test
#     that checks that two appointments produce two messages with the correct text. The test
#     must not print "REAL SMS".
#     Answer: FakeSmsClient only saves (phone, text) in a list. The test gives it to
#     ReminderService, checks the two messages and checks with capsys that "REAL SMS" was not
#     printed.
#
# 10.4 Question: Find one more production problem in this code that has nothing to do with
#     tests.
#     Answer: If send() fails for one appointment (network error, wrong phone number), the
#     exception stops the loop and all patients after it get no reminder, and if we run the job
#     again the first patients get the SMS twice. Now remind() catches the error for one
#     appointment, logs it, goes on with the others and returns the failed ones so they can be
#     sent again. (Also the production API key was written in the code, so it is in git; it
#     must be changed and read from the environment.)
import logging
import os

log = logging.getLogger(__name__)


class SmsClient:
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("SMS API key is missing")
        self.api_key = api_key

    def send(self, phone, text):
        # in production this calls the SMS provider's HTTP API
        print(f"REAL SMS to {phone}: {text}")


class ReminderService:
    def __init__(self, sms_client):
        self._sms = sms_client

    def remind(self, appointments):
        failed = []
        for a in appointments:
            text = f"Reminder: your visit tomorrow at {a['time']}"
            try:
                self._sms.send(a["phone"], text)
            except Exception:
                log.exception("reminder to %s failed", a["phone"])
                failed.append(a)
        return failed


# the real client is created only here, at start-up
def main(appointments):
    sms = SmsClient(api_key=os.environ["SMS_API_KEY"])
    return ReminderService(sms).remind(appointments)


class FakeSmsClient:
    def __init__(self, fail_for=()):
        self.sent = []
        self._fail_for = set(fail_for)

    def send(self, phone, text):
        if phone in self._fail_for:
            raise ConnectionError("provider is down")
        self.sent.append((phone, text))


APPOINTMENTS = [
    {"phone": "+998901112233", "time": "09:30"},
    {"phone": "+998935556677", "time": "14:00"},
]


def test_two_appointments_two_messages(capsys):
    fake = FakeSmsClient()
    failed = ReminderService(fake).remind(APPOINTMENTS)
    assert failed == []
    assert fake.sent == [
        ("+998901112233", "Reminder: your visit tomorrow at 09:30"),
        ("+998935556677", "Reminder: your visit tomorrow at 14:00"),
    ]
    assert "REAL SMS" not in capsys.readouterr().out


def test_one_failure_does_not_stop_the_others():
    fake = FakeSmsClient(fail_for={"+998901112233"})
    failed = ReminderService(fake).remind(APPOINTMENTS)
    assert failed == [APPOINTMENTS[0]]
    assert fake.sent == [("+998935556677", "Reminder: your visit tomorrow at 14:00")]


def test_no_key_in_source(monkeypatch):
    monkeypatch.delenv("SMS_API_KEY", raising=False)
    try:
        main([])
    except KeyError:
        pass
    else:
        raise AssertionError("main() must read the key from the environment")
