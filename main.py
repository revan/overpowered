import rumps

import gcal

APP_TITLE = 'Overpowered'


class OverpoweredApp(rumps.App):

    def __init__(self, *args, **kwargs):
        super(OverpoweredApp, self).__init__(*args, **kwargs)

        self.logout_button = rumps.MenuItem('Logout and Quit')
        self.logout_button.set_callback(self._logout_callback)

    @rumps.timer(5)
    def update_title(self, _):
        events = gcal.fetch_events()
        self.title = events[0].display()
        self.menu.clear()
        self.menu.update(e.display() for e in events[1:])
        self.menu.add(self.logout_button)
        self.menu.add(self.quit_button)

    def _logout_callback(self, _):
        gcal.logout()
        self.quit_button.callback(None)


if __name__ == '__main__':
    app = OverpoweredApp(APP_TITLE)
    app.run()
