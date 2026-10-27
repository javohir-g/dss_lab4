# Lab 4A. Extra task E2 - API tokens in the error tracker
# Student: Javohir Gayratov
#
# E2.1 Question: Print repr() of a User and list everything that leaks.
#     Answer: The generated repr() prints every field:
#         User(user_id=7, email='ali@example.com', password_hash='pbkdf2_sha256$...',
#              api_token='tok_8c1d77e09f2a')
#     The api_token leaks (anyone who reads the log can use the API as this user), the
#     password_hash leaks (it can be cracked offline), and the e-mail is personal data that
#     should not go to an outside error tracker without a reason.
#
# E2.2 Question: Hide password_hash completely, and show api_token masked, with only its last
#     4 characters: tok_****9f2a.
#     Answer: password_hash and api_token have field(repr=False), and my own __repr__ shows the
#     token masked: the prefix before "_" and the last 4 characters, like tok_****9f2a.
#
# E2.3 Question: __str__ is for people (the UI), __repr__ is for developers (the logs). Should
#     they be different here? Write both.
#     Answer: Yes. __str__ is what a person sees in the UI (only the e-mail), __repr__ is for
#     the developer in the logs (id, e-mail, masked token). Both do not show any secret.
#
# E2.4 Question: Does field(repr=False) also remove the field from ==? Check it, and say
#     whether it matters for User.
#     Answer: No, repr=False only removes the field from repr(), == still compares
#     password_hash and api_token. For User it does not leak anything, because == only returns
#     True or False. But two copies of the same user with a new token are "not equal", so to
#     check "same user" we should compare user_id.
from dataclasses import dataclass, field


def mask_token(token):
    if len(token) <= 8:
        return "****"
    prefix = token.split("_", 1)[0] + "_" if "_" in token else ""
    return f"{prefix}****{token[-4:]}"


@dataclass
class User:
    user_id: int
    email: str
    password_hash: str = field(repr=False)
    api_token: str = field(repr=False)

    def __repr__(self):
        return (f"User(user_id={self.user_id!r}, email={self.email!r}, "
                f"api_token={mask_token(self.api_token)!r})")

    def __str__(self):
        return self.email


HASH = "pbkdf2_sha256$600000$Qx7rLm$Zk3n9Vb0aTq1W8c"
TOKEN = "tok_8c1d77e09f2a"


def make_user(**changes):
    values = dict(user_id=7, email="ali@example.com", password_hash=HASH, api_token=TOKEN)
    values.update(changes)
    return User(**values)


def test_no_secret_in_repr_or_str():
    user = make_user()
    for text in (repr(user), str(user), f"{user!r}", "sync failed for %r" % user):
        assert HASH not in text and "pbkdf2" not in text
        assert TOKEN not in text and "8c1d77e0" not in text


def test_masked_token_shows_only_last_4():
    assert repr(make_user()) == "User(user_id=7, email='ali@example.com', api_token='tok_****9f2a')"
    assert mask_token("abcdef1234567890") == "****7890"
    assert mask_token("short") == "****"


def test_str_is_for_people():
    assert str(make_user()) == "ali@example.com"


def test_repr_false_is_still_compared():
    assert make_user() == make_user()
    assert make_user() != make_user(api_token="tok_0000000000aa")
    assert make_user() != make_user(password_hash="other")
