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

