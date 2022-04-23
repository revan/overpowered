import arrow
import dataclasses
import datetime
from dateutil import parser
import os.path
from typing import *
import re

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_PATH = '/tmp/overpowered-token.json'
ZOOM_URL_REGEX = re.compile(r'https?:\/\/(\S*?)\.zoom.us\/j\/(\S+)\?pwd=(\S+?)(?:#|&|$)\S*')


@dataclasses.dataclass(frozen=True)
class CalendarEvent:
    name: str
    start: datetime.datetime
    end: datetime.datetime
    join_link: Optional[str]

    def __post_init__(self):
        # Strip Clockwise emoji.
        if self.name.startswith('❇️ '):
            object.__setattr__(self, 'name', self.name[3:])

    @property
    def display(self) -> str:
        until = self.start_human
        if 'ago' in until:
            return f'{self.name} ends {self.end_human}'
        else:
            return f'{self.name} {until}'

    @property
    def start_human(self) -> str:
        return arrow.get(self.start).humanize()

    @property
    def end_human(self) -> str:
        return arrow.get(self.end).humanize()

    def format_times(self) -> str:
        return f'{self.start.strftime("%I:%M %p")} - {self.end.strftime("%I:%M %p")}'


def _extract_join_link(event: dict) -> Optional[str]:
    conference_link = (
            [
                ep.get('uri') for ep in event.get('conferenceData', {}).get('entryPoints', [])
                if ep.get('entryPointType') == 'video'
            ] + [None]
    )[0]

    if conference_link:
        return conference_link

    match = re.search(ZOOM_URL_REGEX, event.get('description', ''))
    if match:
        return match.group(0)
    return None


def _craft_app_link(join_link: str) -> Optional[str]:
    match = re.match(ZOOM_URL_REGEX, join_link)
    if not match or len(match.groups()) != 3:
        return None
    return f'zoommtg://{match.group(1)}.zoom.us/join?action=join&confno={match.group(2)}&pwd={match.group(3)}&browser=chrome'


def extract_app_link(event: dict) -> Optional[str]:
    join_link = _extract_join_link(event)
    return join_link and _craft_app_link(join_link) or None


def _get_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def _should_prune(event: CalendarEvent) -> bool:
    # Ignore Clockwise padding
    if event.name == 'Focus Time (via Clockwise)':
        return True

    # Ignore full-day events.
    if event.end - event.start > datetime.timedelta(hours=7):
        return True

    return False


def fetch_events(maxResults=10) -> List[CalendarEvent]:
    service = _get_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=maxResults,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    calendar_events = [
        CalendarEvent(
            name=event['summary'],
            start=parser.parse(event['start'].get('dateTime', event['start'].get('date'))),
            end=parser.parse(event['end'].get('dateTime', event['end'].get('date'))),
            join_link=extract_app_link(event),
        )
        for event in events
    ]

    return [
        ce
        for ce in calendar_events
        if not _should_prune(ce)
    ]


def logout() -> None:
    os.remove(TOKEN_PATH)
