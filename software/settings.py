from os import environ

SESSION_CONFIGS = [
    dict(
        name='Feed',
        app_sequence=['DICE'],
        num_demo_participants=3,
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0,
    title = 'Dr.',
    full_name = 'Hauke Roggenkamp',
    eMail = 'Hauke.Roggenkamp@mtec.ethz.ch',
    study_name = 'A study about social media',
    survey_link = 'https://kedgebs.eu.qualtrics.com/jfe/form/SV_8rnrq4PRm5C4ijk',
    dwell_threshold = 75,
    focal_line_position = 0.33,  # vertical position of focal line as share of viewport height (0 = top, 1 = bottom)
    url_param = 'PROLIFIC_PID',
    completion_code = 'ABCDEF',
    data_path = "DICE/static/data/toxic_movie_reactions.csv", # "DICE/static/data/sample_tweets.csv",
    delimiter=',',
    feed_size = 25,
    creatives_path = "DICE/static/creatives",
    num_creatives = 8,
    sort_by='datetime',
    condition_col='condition',
    search_term = "Fire and Ash",
    preloader_delay = 5000,   # milliseconds — loading screen duration
    redirect_delay = 3000,    # milliseconds — auto-redirect delay
    batch_delay = 800,        # milliseconds — simulated network delay between post batches
    trending_topics=[
        {'label': 'FireAndAsh',      'count': '52K Posts'},
        {'label': 'BoxOffice',         'count': '21K Posts'},
        {'label': 'Formula1',         'count': '18K Posts'},
        {'label': 'Champions League',  'count': '95K Posts'},
        {'label': 'MondayMotivation',  'count': '44K Posts'},
        {'label': 'AgenticAI',         'count': '156K Posts'},
    ],
)

PARTICIPANT_FIELDS = ['tweets', 'finished']  # 'tweets' kept for backward-compatibility with existing databases
SESSION_FIELDS = ['prolific_completion_url']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ Welcome """

# Set your own secret key via OTREE_SECRET_KEY environment variable
SECRET_KEY = environ.get('OTREE_SECRET_KEY', '8744361096089')
