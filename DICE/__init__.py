from otree.api import *
import pandas as pd
import numpy as np
import re
import random
import itertools
import urllib.parse
import os
import json


doc = """
Mimic social media feeds with DICE.
"""


class C(BaseConstants):
    NAME_IN_URL = 'DICE'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    RULES_TEMPLATE = "DICE/T_Rules.html"
    CONSENT_TEMPLATE = "DICE/T_Consent.html"
    TOPICS_TEMPLATE = "DICE/T_Trending_Topics.html"
    ITEM_POST = "DICE/T_Item_Post.html"

class Subsession(BaseSubsession):
    feed_conditions = models.StringField(doc='indicates the feed condition a player is randomly assigned to')

class Group(BaseGroup):
    pass


class Player(BasePlayer):
    feed_condition = models.StringField(doc='indicates the feed condition a player is randomly assigned to')
    feed_toxicity = models.FloatField(doc='mean toxicity score of the feed shown to this player', blank=True)
    sequence = models.StringField(doc='prints the sequence of posts based on doc_id')

    dwell_data = models.LongStringField(doc='tracks the time feed items were visible in a participants viewport.', blank=True)
    focal_line_data = models.LongStringField(doc='tracks cumulative time each post spent covering the focal line.', blank=True)
    rowheight_data = models.LongStringField(doc='tracks the height of feed items in pixels.', blank=True)
    likes_data = models.LongStringField(doc='tracks likes.', blank=True)
    replies_data = models.LongStringField(doc='tracks replies.', blank=True)
    lottery_signup = models.BooleanField(doc='indicates whether the participant entered the Disney+ lottery draw.', blank=True)
    time_on_feed = models.FloatField(doc='seconds spent browsing the feed, from preloader hide to submit click.', blank=True)
    creative_image = models.LongStringField(doc='JSON mapping of doc_id to creative media path for posts with assigned creatives.', blank=True)

    is_touch_device = models.BooleanField(doc="indicates whether a participant uses a touch device to access survey.",
                                           blank=True)
    device_type = models.StringField(doc="indicates the participant's device type based on screen width.",
                                           blank=True)
    screen_resolution = models.StringField(doc="indicates the participant's screen resolution, i.e., width x height.",
                                           blank=True)


# FUNCTIONS -----
def creating_session(subsession):
    # Load and preprocess data once but shuffle and assign for each player
    df = read_feed(path=subsession.session.config['data_path'], delim=subsession.session.config['delimiter'])
    processed_posts = preprocessing(df, subsession.session.config)

    # Check if the file contains any conditions and assign groups to it
    condition = subsession.session.config['condition_col']
    if condition in processed_posts.columns:
        feed_conditions = itertools.cycle(processed_posts[condition].unique())
        subsession.feed_conditions = ', '.join(processed_posts[condition].unique())

    players = subsession.get_players()
    feed_size = subsession.session.config.get('feed_size', 0)

    # Load creative images if available
    creatives_path = subsession.session.config.get('creatives_path', '')
    creatives = []
    creatives_are_local = False
    if creatives_path:
        if os.path.isdir(creatives_path):
            image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
            folder = os.path.basename(creatives_path.rstrip('/\\'))
            creatives = [
                f'{folder}/{f}'
                for f in sorted(os.listdir(creatives_path))
                if os.path.splitext(f)[1].lower() in image_exts
            ]
            creatives_are_local = True
        else:
            try:
                creatives = pd.read_csv(creatives_path)['url'].dropna().tolist()
            except Exception:
                pass
    num_creatives = subsession.session.config.get('num_creatives', 5)

    # Prepare uniformly spaced toxicity targets if feed_size is configured
    toxicity_targets = None
    if feed_size > 0 and 'toxicity' in processed_posts.columns:
        n_players = len(players)
        tox_min = processed_posts['toxicity'].min()
        tox_max = processed_posts['toxicity'].max()
        toxicity_targets = np.linspace(tox_min, tox_max, n_players)
        np.random.shuffle(toxicity_targets)

    for i, player in enumerate(players):
        # Deep copy the DataFrame to ensure each player gets a unique shuffled version
        posts = processed_posts.copy()

        # Assign a condition to the player if conditions are present
        if condition in posts.columns:
            player.feed_condition = next(feed_conditions)
            condition_mask = posts[condition] == player.feed_condition
            # Always keep fixed-position posts regardless of their condition value
            if 'fixed_position' in posts.columns:
                condition_mask = condition_mask | posts['fixed_position'].notna()
            posts = posts[condition_mask]

        # Sample a subset of posts by toxicity if configured
        if toxicity_targets is not None:
            posts = sample_feed_by_toxicity(posts, toxicity_targets[i], feed_size)
            regular = posts[posts['fixed_position'].isna()] if 'fixed_position' in posts.columns else posts
            player.feed_toxicity = float(round(regular['toxicity'].mean(), 4))

        # Shuffle post order and assign sequential ranks
        posts = posts.sample(frac=1).reset_index(drop=True)
        posts['sequence'] = np.arange(1, len(posts) + 1)

        # Randomly attach creative images to a subset of posts
        if creatives and num_creatives > 0:
            img_indices = np.random.choice(len(posts), size=min(num_creatives, len(posts)), replace=False)
            chosen_urls = np.random.choice(creatives, size=len(img_indices), replace=len(img_indices) > len(creatives))
            posts.loc[img_indices, 'media'] = chosen_urls
            posts.loc[img_indices, 'pic_available'] = True
            posts.loc[img_indices, 'media_is_local'] = creatives_are_local
            player.creative_image = json.dumps({
                str(row['doc_id']): row['media']
                for _, row in posts.loc[img_indices].iterrows()
            })

        # Assign processed posts to player-specific variable
        # (participant field kept as 'tweets' for backward-compatibility with existing databases)
        player.participant.tweets = posts

        # Record the sequence for each player
        player.sequence = ', '.join(map(str, posts['doc_id'].tolist()))


def read_feed(path, delim):
    if re.match(r'^https?://\S+', path):
        if 'github' in path:
            posts = pd.read_csv(path, sep=delim)
        elif 'drive.google.com' in path:
            if '/uc?' in path:
                # Already in the correct format
                posts = pd.read_csv(path, sep=delim)
            else:
                # Convert from /file/d/ format
                file_id = path.split('/')[-2]
                download_url = f'https://drive.google.com/uc?id={file_id}'
                posts = pd.read_csv(download_url, sep=delim)
        else:
            raise ValueError("Unrecognized URL format")
    else:
        posts = pd.read_csv(path, sep=delim)
    return posts


# Check if a string is a URL (starts with http)
def is_url(s):
    return bool(re.match(r'^https?:\/\/', str(s)))


def format_dates(df):
    """Parse and format date columns."""
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce', format='mixed')
    mask = df['datetime'].isna()
    if mask.any():
        df.loc[mask, 'datetime'] = pd.to_datetime(
            df.loc[mask, 'datetime'],
            errors='coerce',
            format='%d.%m.%y %H:%M'
        )
    df['date'] = df['datetime'].dt.strftime('%d %b').str.replace(' ', '. ')
    df['date'] = df['date'].str.lstrip('0')
    df['formatted_datetime'] = df['datetime'].dt.strftime('%I:%M %p · %b %d, %Y')
    return df


def highlight_entities(df):
    """Highlight hashtags, cashtags, mentions, and URLs in post text."""
    df['text'] = df['text'].str.replace(r'\B(\#[a-zA-Z0-9_]+\b)',
                                        r'<span class="text-primary">\g<0></span>', regex=True)
    df['text'] = df['text'].str.replace(r'\B(\$[a-zA-Z0-9_\.]+\b)',
                                        r'<span class="text-primary">\g<0></span>', regex=True)
    df['text'] = df['text'].str.replace(r'\B(\@[a-zA-Z0-9_]+\b)',
                                        r'<span class="text-primary">\g<0></span>', regex=True)
    # remove the href below, if you don't want them to leave your page
    df['text'] = df['text'].str.replace(
        r'(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])',
        r'<a class="text-primary">\g<0></a>', regex=True)
    return df


def prepare_numeric_fields(df):
    """Convert replies/reposts/likes to int, filling NAs with 0."""
    df['replies'] = df['replies'].fillna(0).astype(int)
    df['reposts'] = df['reposts'].fillna(0).astype(int)
    df['likes'] = df['likes'].fillna(0).astype(int)
    return df


def prepare_media(df):
    """Clean media URLs and set pic_available flag."""
    df['media'] = df['media'].astype(str).str.replace("'|,", '', regex=True)
    # Any non-empty, non-nan value means media is available (URL or local path)
    df['pic_available'] = df['media'].apply(
        lambda m: bool(m and m.strip() and m not in ('nan', 'None', ''))
    )
    # Local if pic is available but not a URL
    df['media_is_local'] = df['pic_available'] & ~df['media'].str.startswith('http')
    return df


def prepare_user_profiles(df):
    """Prepare profile pics, icons, colors, descriptions, followers, and tooltip HTML."""
    df['profile_pic_available'] = False
    df['icon'] = df['username'].str[:2].str.title()

    # Assign a deterministic color class based on username hash
    color_classes = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']
    df['color_class'] = df['username'].apply(
        lambda name: color_classes[hash(name) % len(color_classes)]
    )

    # make sure user descriptions do not entail any '' or "" as this complicates visualization
    # also replace nan with some whitespace
    df['user_description'] = df['user_description'].str.replace("'", '')
    df['user_description'] = df['user_description'].str.replace('"', '')
    df['user_description'] = df['user_description'].fillna(' ')

    # make number of followers a formatted string
    df['user_followers'] = df['user_followers'].map('{:,.0f}'.format).str.replace(',', '.')

    # Build tooltip HTML once per row
    df['tooltip_html'] = (
        "<div class='text-start text-secondary'><b class='text-dark'>" + df['username'] + "</b><br>"
        "@" + df['handle'] + "<br><br>"
        + df['user_description'] + " <br><br><b class='text-dark'>" + df['user_followers'] + "</b> Followers</div>"
    )

    return df


def extract_toxicity(df):
    """Extract Perspective API toxicity scores from user_description into a numeric column."""
    scores = df['user_description'].str.extract(r'Score:\s*([\d.]+)')
    if scores[0].notna().any():
        df['toxicity'] = pd.to_numeric(scores[0], errors='coerce')
    return df


def sample_feed_by_toxicity(posts, target_mean, feed_size, sigma=0.15):
    """Sample feed_size posts with mean toxicity close to target_mean.

    Fixed-position posts (e.g. ads) are always included and excluded from
    the sampling pool so they don't distort toxicity weights.
    """
    if 'fixed_position' in posts.columns:
        fixed = posts[posts['fixed_position'].notna()]
        regular = posts[posts['fixed_position'].isna()]
    else:
        fixed = pd.DataFrame()
        regular = posts

    if feed_size >= len(regular):
        return posts.copy()

    scores = regular['toxicity'].values
    weights = np.exp(-0.5 * ((scores - target_mean) / sigma) ** 2)
    weights /= weights.sum()
    indices = np.random.choice(len(regular), size=feed_size, replace=False, p=weights)
    sampled = regular.iloc[sorted(indices)]

    if not fixed.empty:
        return pd.concat([sampled, fixed]).copy()
    return sampled.copy()


def preprocessing(df, config):
    """Orchestrate all preprocessing steps."""
    df = format_dates(df)
    df = highlight_entities(df)
    df = prepare_numeric_fields(df)
    df = prepare_media(df)
    df = prepare_user_profiles(df)
    df = extract_toxicity(df)

    # Check if 'condition_col' is set and not empty, and if it's an existing column in df
    if ('condition_col' in config and
            config['condition_col'] and
            config['condition_col'] in df.columns):
        df.rename(columns={config['condition_col']: 'condition'}, inplace=True)

    return df


def create_redirect(player):
    """Build the survey redirect URL with query parameters."""
    participant_id = player.participant.label or player.participant.code
    params = {player.session.config['url_param']: participant_id}

    completion_code = player.session.vars.get('completion_code')
    if completion_code is not None:
        params['cc'] = completion_code

    if player.feed_condition is not None:
        params['condition'] = player.feed_condition

    return player.session.config['survey_link'] + '?' + urllib.parse.urlencode(params)


# PAGES
class A_Intro(Page):
    form_model = 'player'

    @staticmethod
    def before_next_page(player, timeout_happened):
        # update sequence
        df = player.participant.tweets
        posts = df[df['condition'] == player.feed_condition]
        player.sequence = ', '.join(map(str, posts['doc_id'].tolist()))

class B_Briefing(Page):
    form_model = 'player'


class C_Feed(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        fields = ['likes_data', 'replies_data', 'lottery_signup', 'time_on_feed', 'is_touch_device',
                  'device_type', 'screen_resolution', 'dwell_data', 'focal_line_data', 'rowheight_data']
        return fields

    @staticmethod
    def vars_for_template(player: Player):
        label_available = player.participant.label is not None
        posts_df = player.participant.tweets.reset_index(drop=True)

        if 'fixed_position' in posts_df.columns and posts_df['fixed_position'].notna().any():
            fixed = posts_df[posts_df['fixed_position'].notna()].copy()
            regular = posts_df[posts_df['fixed_position'].isna()].copy()

            # Fixed-position posts must pass the condition check in the template
            fixed['condition'] = player.feed_condition

            # Insert fixed posts at their specified 1-indexed positions
            posts_list = regular.to_dict('records')
            for _, row in fixed.sort_values('fixed_position').iterrows():
                pos = min(int(row['fixed_position']) - 1, len(posts_list))
                posts_list.insert(pos, row.to_dict())

            posts = {i: row for i, row in enumerate(posts_list)}
        else:
            posts = posts_df.to_dict('index')

        return dict(
            posts=posts,
            search_term=player.session.config['search_term'],
            label_available=label_available,
            trending_topics=player.session.config.get('trending_topics', []),
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            dwell_threshold=player.session.config['dwell_threshold'],
            focal_line_position=player.session.config.get('focal_line_position', 0.33),
            preloader_delay=player.session.config.get('preloader_delay', 5000),
            batch_delay=player.session.config.get('batch_delay', 800),
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.finished = True

        completion_code = player.session.vars.get('completion_code')
        base_url = 'https://app.prolific.com/submissions/complete'
        if player.session.vars.get('prolific_completion_url') is not None:
            player.session.vars['prolific_completion_url'] = (
                f'{base_url}?cc={completion_code}' if completion_code else base_url
            )
        else:
            player.session.vars['prolific_completion_url'] = 'NA'

        if player.id_in_group != 1:
            player.participant.tweets = ""


class D_Redirect(Page):

    @staticmethod
    def is_displayed(player):
        return len(player.session.config['survey_link']) > 0

    @staticmethod
    def vars_for_template(player: Player):
        return dict(link=create_redirect(player))

    @staticmethod
    def js_vars(player):
        return dict(
            link=create_redirect(player),
            redirect_delay=player.session.config.get('redirect_delay', 3000),
        )

class D_Debrief(Page):

    @staticmethod
    def is_displayed(player):
        return len(player.session.config['survey_link']) == 0

page_sequence = [A_Intro,
                 B_Briefing,
                 C_Feed,
                 D_Redirect,
                 D_Debrief]


def _parse_json_field(value):
    """Parse a JSON string field, returning an empty list on failure."""
    if not value or len(value) <= 1:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def custom_export(players):
    yield [
        'session_code', 'participant_code', 'participant_label',
        'condition', 'feed_toxicity', 'lottery_signup', 'time_on_feed',
        'device_type', 'is_touch_device', 'screen_resolution', 'time_started', 'completed_feed',
        'doc_id', 'displayed_sequence',
        'dwell_time', 'focal_dwell_time', 'liked', 'reply', 'has_reply', 'post_height_px', 'creative_image',
    ]

    for p in players:
        if not p.sequence:
            continue

        # --- participant-level fields ---
        ts = getattr(p.participant, '_start_timestamp', None)
        time_started = str(pd.Timestamp(ts, unit='s'))[:19] if ts else None

        # --- sequence: list of doc_ids in display order ---
        seq_list = [int(x.strip()) for x in p.sequence.split(',') if x.strip()]
        seq_map = {doc_id: i + 1 for i, doc_id in enumerate(seq_list)}

        # --- viewport: sum durations per doc_id ---
        viewport_map = {}
        for entry in _parse_json_field(p.dwell_data):
            doc_id = entry.get('doc_id')
            if doc_id is not None:
                viewport_map[int(doc_id)] = round(
                    viewport_map.get(int(doc_id), 0) + entry.get('duration', 0), 3)

        # --- focal line ---
        focal_map = {}
        for entry in _parse_json_field(p.focal_line_data):
            doc_id = entry.get('doc_id')
            if doc_id is not None:
                focal_map[int(doc_id)] = round(
                    focal_map.get(int(doc_id), 0) + entry.get('duration', 0), 3)

        # --- likes ---
        likes_map = {int(e['doc_id']): e.get('liked', False)
                     for e in _parse_json_field(p.likes_data) if 'doc_id' in e}

        # --- replies ---
        replies_map = {int(e['doc_id']): (e.get('reply', ''), e.get('hasReply', False))
                       for e in _parse_json_field(p.replies_data) if 'doc_id' in e}

        # --- rowheights ---
        rowheight_map = {int(e['doc_id']): e.get('height')
                         for e in _parse_json_field(p.rowheight_data) if 'doc_id' in e}

        # --- creative assignments ---
        creative_map = {}
        if p.creative_image:
            try:
                creative_map = {int(k): v for k, v in json.loads(p.creative_image).items()}
            except Exception:
                pass

        # --- one row per post ---
        for doc_id in seq_list:
            reply_text, has_reply = replies_map.get(doc_id, (None, None))
            yield [
                p.session.code,
                p.participant.code,
                p.participant.label,
                p.feed_condition,
                p.feed_toxicity,
                p.lottery_signup,
                p.time_on_feed,
                p.device_type,
                p.is_touch_device,
                p.screen_resolution,
                time_started,
                p.participant.vars.get('finished', False),
                doc_id,
                seq_map.get(doc_id),
                viewport_map.get(doc_id),
                focal_map.get(doc_id),
                likes_map.get(doc_id),
                reply_text or None,
                has_reply or None,
                rowheight_map.get(doc_id),
                creative_map.get(doc_id),
            ]
