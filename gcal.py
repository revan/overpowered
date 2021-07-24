import arrow
import dataclasses
import datetime
from dateutil import parser

import os.path
from typing import *

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_PATH = '/tmp/overpowered-token.json'


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

    def display(self) -> str:
        until = self.start_human()
        if 'ago' in until:
            return f'{self.name} ends {self.end_human()}'
        else:
            return f'{self.name} {until}'

    def start_human(self) -> str:
        return arrow.get(self.start).humanize()

    def end_human(self) -> str:
        return arrow.get(self.end).humanize()

    def format_times(self) -> str:
        return f'{self.start.strftime("%I:%M %p")} - {self.end.strftime("%I:%M %p")}'


def _extract_join_link(event: dict):
    # TODO also look for link in event description
    return ([ep.get('uri') for ep in event.get('conferenceData', {}).get('entryPoints', [])
             if ep.get('entryPointType') == 'video'] + [None])[0]


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


def fetch_events(maxResults=10):
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

    return [
        CalendarEvent(
            name=event['summary'],
            start=parser.parse(event['start'].get('dateTime', event['start'].get('date'))),
            end=parser.parse(event['end'].get('dateTime', event['end'].get('date'))),
            join_link=_extract_join_link(event),
        )
        for event in events
    ]


def logout():
    os.remove(TOKEN_PATH)
