from setuptools import setup


APP = ['main.py']
DATA_FILES = ['client_secret.json']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'googleapiclient', 'google_auth_oauthlib', 'arrow'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
