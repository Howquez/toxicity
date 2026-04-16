from os import environ

SESSION_CONFIGS = [
    dict(
        name='ratings',
        display_name='Toxicity Rating (Validation)',
        app_sequence=['ratings'],
        num_demo_participants=3,
        seed=230691,
        completion_code='',   # set before launching on Prolific
    ),
]

ROOMS = [
    dict(
        name='prolific_ratings',
        display_name='Toxicity Rating (Prolific)',
    ),
]

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.75,
    doc="",
)

PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'GBP'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = ""

SECRET_KEY = '1862378455910'
