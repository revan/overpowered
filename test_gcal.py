import arrow
from arrow.arrow import timedelta

import pytest

from gcal import CalendarEvent
from gcal import _craft_app_link


def test_craft_app_link():
    join_link = "https://orgname.zoom.us/j/123456789?pwd=jkf3F28HJhjk998FJksBsFQfwrLn"
    app_link = _craft_app_link(join_link=join_link)

    assert app_link == "zoommtg://orgname.zoom.us/join?action=join&confno=123456789&pwd=jkf3F28HJhjk998FJksBsFQfwrLn&browser=chrome"


def test_craft_app_link_strips_anchors():
    join_link = "https://orgname.zoom.us/j/123456789?pwd=jkf3F28HJhjk998FJksBsFQfwrLn#success"
    app_link = _craft_app_link(join_link=join_link)

    assert app_link == "zoommtg://orgname.zoom.us/join?action=join&confno=123456789&pwd=jkf3F28HJhjk998FJksBsFQfwrLn&browser=chrome"


def test_craft_app_link_handles_errors():
    join_link = "https://www.google.com"
    app_link = _craft_app_link(join_link=join_link)

    assert app_link is None


@pytest.mark.parametrize("delta,text", [
    (timedelta(days=3), "Event in 3 days"),
    (timedelta(hours=24), "Event in a day"),
    (timedelta(hours=5), "Event in 5 hours"),
    (timedelta(hours=1, minutes=30), "Event in an hour"),
    (timedelta(hours=1), "Event in an hour"),
    (timedelta(minutes=57), "Event in 57 minutes"),
    (timedelta(minutes=2), "Event in 2 minutes"),
    (timedelta(minutes=1), "Event in a minute"),
    (timedelta(seconds=10), "Event in 10 seconds"),
    (timedelta(seconds=3), "Event just now"),
    (timedelta(), "Event just now"),
    (timedelta(seconds=-10), "Event ends in an hour"),
    (timedelta(minutes=-1), "Event ends in an hour"),
    (timedelta(minutes=-2), "Event ends in an hour"),
    (timedelta(minutes=-57), "Event ends in an hour"),
    (timedelta(hours=-1), "Event ends in an hour"),
    (timedelta(hours=-1, minutes=-30), "Event ends in 30 minutes"),
    (timedelta(hours=-1, minutes=-55), "Event ends in 5 minutes"),
    (timedelta(hours=-1, minutes=-59), "Event ends in a minute"),
    (timedelta(hours=-1, minutes=-59, seconds=-50), "Event ends in 10 seconds"),
    (timedelta(hours=-1, minutes=-59, seconds=-55), "Event ends just now"),
    (timedelta(hours=-2), "Event ends just now"),
])
def test_time_display(delta: timedelta, text: str):
    now = arrow.utcnow()

    event = CalendarEvent(
        name="Event",
        start=(now + delta).datetime,
        end=(now + delta + timedelta(hours=2)).datetime,
        join_link=None,
    )

    assert event.display == text
