import rumps

import gcal


class OverpoweredApp(rumps.App):

    @rumps.timer(5)
    def update_title(self, sender):
        events = gcal.fetch_events()
        self.title = events[0].display()
        self.menu.clear()
        self.menu.update(e.display() for e in events[1:])
        self.menu.add(self.quit_button)


if __name__ == '__main__':
    app = OverpoweredApp("Overpowered")
    app.run()
