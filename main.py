import arrow
import json
import webbrowser

import rumps

import gcal

APP_TITLE = 'Overpowered'

ACTIVATION_TYPE_ACTION = 2


class OverpoweredApp(rumps.App):

    def __init__(self, *args, **kwargs):
        super(OverpoweredApp, self).__init__(*args, **kwargs)

        self.logout_button = rumps.MenuItem('Logout and Quit')
        self.logout_button.set_callback(self._logout_callback)

        self.join_link = None
        self.join_button = rumps.MenuItem('Join next meeting')
        self._have_notified = set()

    @rumps.timer(5)
    def update_loop(self, _):
        events = gcal.fetch_events()

        self.menu.clear()
        if events:
            self.title = events[0].display
            if events[0].join_link:
                self.join_link = events[0].join_link
                self.join_button.set_callback(self._join_callback)
                self.menu.add(self.join_button)
            else:
                self.menu.add("No link for next meeting.")
        self.menu.add(None)
        self.menu.update(e.display for e in events[1:] if arrow.get(e.end) < arrow.utcnow().shift(days=1))
        self.menu.add(None)
        self.menu.add(self.logout_button)
        self.menu.add(self.quit_button)

        if events:
            about_to_start = (arrow.get(events[0].start) > arrow.utcnow() and
                              arrow.get(events[0].start) - arrow.utcnow() < arrow.arrow.timedelta(minutes=1))
            mid_event = (arrow.get(events[0].start)
                         < arrow.utcnow()
                         < arrow.get(events[0].end) - arrow.arrow.timedelta(minutes=1))
            about_to_end = (arrow.get(events[0].end) > arrow.utcnow() and
                            arrow.get(events[0].end) - arrow.utcnow() < arrow.arrow.timedelta(minutes=1))
            if about_to_start or mid_event:
                self._maybe_send_notification(events[0])
            elif about_to_end and len(events) > 1:
                # Special handling to notify of next event during current event for subsequent (or overlapping) events.
                about_to_start = (arrow.get(events[1].start) > arrow.utcnow() and
                                  arrow.get(events[1].start) - arrow.utcnow() < arrow.arrow.timedelta(minutes=1))
                mid_event = (arrow.get(events[1].start)
                             < arrow.utcnow()
                             < arrow.get(events[1].end) - arrow.arrow.timedelta(minutes=1))
                if about_to_start or mid_event:
                    self._maybe_send_notification(events[1])
        else:
            self.title = 'No upcoming events.'

    def _maybe_send_notification(self, event: gcal.CalendarEvent):
        if event not in self._have_notified:
            if event.join_link:
                rumps.notification(
                    title=event.name,
                    subtitle=event.format_times(),
                    message="Join Zoom call",
                    action_button="Join",
                    sound=True,
                    data={'url': event.join_link},
                )
            else:
                rumps.notification(
                    title=event.name,
                    subtitle=event.format_times(),
                    message="No Zoom link",
                    sound=True,
                    data={},
                )
            self._have_notified.add(event)

    @rumps.notifications
    def handle_notification(self, notification):
        if notification.get('activationType') == ACTIVATION_TYPE_ACTION and notification.get('url'):
            webbrowser.open(notification.get('url'))



    def _logout_callback(self, _):
        gcal.logout()
        self.quit_button.callback(None)

    def _join_callback(self, _):
        webbrowser.open(self.join_link)


if __name__ == '__main__':
    app = OverpoweredApp(APP_TITLE)
    app.serializer = json
    app.run()
