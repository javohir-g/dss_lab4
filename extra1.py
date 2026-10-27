# Lab 4A. Extra task E1 - Someone changed the settings at runtime
# Student: Javohir Gayratov
#
# E1.1 Question: Write Settings as @dataclass(frozen=True) with three fields: env ('dev',
#     'staging' or 'prod'), max_upload_mb (from 1 to 100) and db_url.
#     Answer: Done below.
#
# E1.2 Question: Check the values in __post_init__, so that a wrong configuration stops the
#     program at start-up.
#     Answer: __post_init__ checks env, max_upload_mb (int from 1 to 100) and db_url (not
#     empty), so a wrong configuration raises ValueError when the program starts.
#
# E1.3 Question: Show that settings.max_upload_mb = 500 now fails. Which exception do you get?
#     Answer: dataclasses.FrozenInstanceError: cannot assign to field 'max_upload_mb'. It is a
#     subclass of AttributeError.
#
# E1.4 Question: One handler really needs a different limit. Get a changed copy with
#     dataclasses.replace() without touching the shared object. Does replace() run your checks
#     again? Prove it with a test.
#     Answer: replace(settings, max_upload_mb=80) returns a new object and the shared one does
#     not change. Yes, replace() makes the copy through __init__, so __post_init__ runs again:
#     replace(settings, max_upload_mb=500) raises ValueError (test_replace_returns_a_checked_copy).
from dataclasses import FrozenInstanceError, dataclass, replace

import pytest


@dataclass(frozen=True)
class Settings:
    ENVIRONMENTS = ("dev", "staging", "prod")

    env: str
    max_upload_mb: int
    db_url: str

    def __post_init__(self):
        if self.env not in self.ENVIRONMENTS:
            raise ValueError(f"env must be one of {self.ENVIRONMENTS}, got {self.env!r}")
        if isinstance(self.max_upload_mb, bool) or not isinstance(self.max_upload_mb, int):
            raise ValueError(f"max_upload_mb must be an int, got {self.max_upload_mb!r}")
        if not 1 <= self.max_upload_mb <= 100:
            raise ValueError(f"max_upload_mb must be 1..100, got {self.max_upload_mb}")
        if not self.db_url:
            raise ValueError("db_url is empty")


def make_settings(**changes):
    values = dict(env="prod", max_upload_mb=20, db_url="postgresql://db.local/lms")
    values.update(changes)
    return Settings(**values)


def test_changing_a_field_raises():
    settings = make_settings()
    with pytest.raises(FrozenInstanceError):
        settings.max_upload_mb = 500
    assert issubclass(FrozenInstanceError, AttributeError)
    assert settings.max_upload_mb == 20


@pytest.mark.parametrize("changes", [
    {"env": "production"}, {"env": "PROD"}, {"max_upload_mb": 0}, {"max_upload_mb": 101},
    {"max_upload_mb": 20.5}, {"max_upload_mb": True}, {"db_url": ""},
])
def test_wrong_configuration_fails_at_start_up(changes):
    with pytest.raises(ValueError):
        make_settings(**changes)


def test_replace_returns_a_checked_copy():
    shared = make_settings()
    big = replace(shared, max_upload_mb=80)
    assert big.max_upload_mb == 80
    assert shared.max_upload_mb == 20 and big is not shared
    with pytest.raises(ValueError):
        replace(shared, max_upload_mb=500)
