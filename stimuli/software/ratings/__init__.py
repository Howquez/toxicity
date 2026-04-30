import json
import random
import pandas as pd
from pathlib import Path
from otree.api import *

doc = """
Human validation of Perspective API and GPT-4o-mini toxicity scores.
Participants rate 100 posts (stratified across 10 Perspective score bins)
on a continuous 0-100 toxicity slider. Three attention-check posts are
embedded at fixed positions. Designed for Prolific delivery.
"""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class C(BaseConstants):
    NAME_IN_URL      = 'ratings'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS       = 1

    POSTS_PER_BIN         = 10   # posts drawn per Perspective score bin into corpus
    N_BINS                = 10   # number of bins (0-0.1, 0.1-0.2, ..., 0.9-1.0)
    POSTS_PER_PARTICIPANT = 36   # posts shown to each participant (subset of corpus)
    POSTS_PER_PAGE        = 6    # posts shown per rating page

    # Attention check posts (not from the corpus)
    ATTN_CIVIL = {
        "doc_id":  "attn_civil",
        "text":    "Just got out of the cinema. Really beautiful film, the world-building is unlike anything I've seen. Highly recommend.",
        "is_attn": True,
        "attn_type": "civil",
    }
    ATTN_TOXIC = {
        "doc_id":  "attn_toxic",
        "text":    "Everyone who paid to see this garbage deserves to be humiliated. The director is a talentless hack and the fans are braindead sheep.",
        "is_attn": True,
        "attn_type": "toxic",
    }
    # Attention check thresholds (scale: 0 to 100)
    ATTN_CIVIL_MAX = 40   # exclude if civil check rated above this
    ATTN_TOXIC_MIN = 60   # exclude if toxic check rated below this


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    prolific_pid    = models.StringField(blank=True)
    ratings_json    = models.LongStringField(blank=True)   # JSON: {doc_id: rating, ...}
    post_order_json = models.LongStringField(blank=True)   # JSON list of doc_ids in display order
    current_page_idx = models.IntegerField(initial=0)      # which rating page the player is on
    time_on_task    = models.FloatField(blank=True)

    # Attention check ratings (stored separately for easy exclusion)
    attn_civil_rating = models.IntegerField(blank=True)
    attn_toxic_rating = models.IntegerField(blank=True)

    # Closing questions
    film_familiarity  = models.IntegerField(
        choices=[[1, "Never heard of it"], [2, "Heard of it but haven't seen it"], [3, "Seen it"]],
        blank=True,
        label="How familiar are you with Avatar: Fire and Ash (the film the posts were about)?",
    )
    task_difficulty = models.IntegerField(
        choices=range(1, 8),
        blank=True,
        label="How difficult did you find the rating task? (1 = very easy, 7 = very difficult)",
    )
    open_feedback = models.LongStringField(
        blank=True,
        label="Is there anything about the task or the posts you would like to flag for our attention? (optional)",
    )

    # Realism ratings: JSON {doc_id: rating} for the 3 sampled posts
    realism_json      = models.LongStringField(blank=True)
    realism_posts_json = models.LongStringField(blank=True)  # JSON list of 3 post dicts

    @property
    def failed_attention(self):
        civil = self.attn_civil_rating
        toxic = self.attn_toxic_rating
        if civil is None or toxic is None:
            return False
        return civil > C.ATTN_CIVIL_MAX or toxic < C.ATTN_TOXIC_MIN


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_corpus():
    """Read the pre-sampled corpus CSV bundled with the app."""
    path = Path(__file__).parent / 'corpus.csv'
    df = pd.read_csv(path)
    records = []
    for _, row in df.iterrows():
        records.append({
            'doc_id':       int(row['doc_id']),
            'text':         str(row['text']),
            'toxicity':     float(row['toxicity']),
            'gpt_toxicity': float(row['gpt_toxicity']) if pd.notna(row.get('gpt_toxicity')) else None,
            'bin':          int(row['bin']),
            'is_attn':      False,
            'attn_type':    None,
        })
    return records


def sample_participant_posts(corpus_posts, seed):
    """
    Stratified subsample of POSTS_PER_PARTICIPANT posts from the corpus.
    Each bin contributes either floor or ceil(POSTS_PER_PARTICIPANT / N_BINS)
    posts; which bins get the extra post is determined by the player seed.
    """
    from collections import defaultdict
    bins = defaultdict(list)
    for p in corpus_posts:
        bins[p['bin']].append(p)

    rng = random.Random(seed)
    bin_keys  = sorted(bins.keys())
    n_present = len(bin_keys)
    base  = C.POSTS_PER_PARTICIPANT // n_present
    extra = C.POSTS_PER_PARTICIPANT  % n_present

    rng.shuffle(bin_keys)
    counts = {b: base + (1 if i < extra else 0) for i, b in enumerate(bin_keys)}

    sampled = []
    for b in sorted(bins.keys()):
        pool = bins[b]
        n = min(counts[b], len(pool))
        sampled.extend(rng.sample(pool, n))
    return sampled


def build_post_order(posts, seed):
    """
    Shuffle posts and insert the two attention checks at fixed positions
    (indices 9 and 25 in the final 38-item sequence).
    Returns the full ordered list.
    """
    rng = random.Random(seed)
    shuffled = posts[:]
    rng.shuffle(shuffled)

    # Insert attention checks: ~1/4 and ~2/3 through the sequence
    attn_positions = {9: C.ATTN_CIVIL, 25: C.ATTN_TOXIC}
    for pos in sorted(attn_positions):
        item = dict(attn_positions[pos])
        shuffled.insert(pos, item)

    return shuffled


def creating_session(subsession):
    corpus_posts = load_corpus()
    seed = subsession.session.config.get('seed', 42)

    for player in subsession.get_players():
        player_seed = seed + player.id_in_subsession
        subset = sample_participant_posts(corpus_posts, player_seed)
        order  = build_post_order(subset, player_seed)
        player.post_order_json = json.dumps(order)
        player.ratings_json    = json.dumps({})


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class A_Intro(Page):
    @staticmethod
    def vars_for_template(player):
        player.prolific_pid = player.participant.label or ''
        return {}


class A2_Examples(Page):
    pass


class B_Rating(Page):
    form_model  = 'player'
    form_fields = ['current_page_idx']

    @staticmethod
    def live_method(player, data):
        ratings = json.loads(player.ratings_json or '{}')
        ratings.update({str(k): v for k, v in data.items()})
        player.ratings_json = json.dumps(ratings)

    @staticmethod
    def vars_for_template(player):
        order = json.loads(player.post_order_json)
        n_pages = -(-len(order) // C.POSTS_PER_PAGE)   # ceiling division
        return dict(
            posts_json   = player.post_order_json,
            n_posts      = len(order),
            posts_per_page = C.POSTS_PER_PAGE,
            n_pages      = n_pages,
        )

    @staticmethod
    def js_vars(player):
        return dict(
            posts          = json.loads(player.post_order_json),
            posts_per_page = C.POSTS_PER_PAGE,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Extract attention check ratings from the ratings dict
        ratings = json.loads(player.ratings_json or '{}')
        civil = ratings.get(C.ATTN_CIVIL['doc_id'])
        toxic = ratings.get(C.ATTN_TOXIC['doc_id'])
        if civil is not None:
            player.attn_civil_rating = int(civil)
        if toxic is not None:
            player.attn_toxic_rating = int(toxic)

        # Sample 3 non-attention-check posts for the realism page
        order = json.loads(player.post_order_json or '[]')
        organic = [p for p in order if not p.get('is_attn')]
        seed = player.session.config.get('seed', 42) + player.id_in_subsession
        rng  = random.Random(seed + 999)
        sample = rng.sample(organic, min(3, len(organic)))
        player.realism_posts_json = json.dumps(sample)


class C_Realism(Page):
    form_model  = 'player'
    form_fields = []   # ratings arrive via live_method

    @staticmethod
    def live_method(player, data):
        realism = json.loads(player.realism_json or '{}')
        realism.update({str(k): v for k, v in data['realism'].items()})
        player.realism_json = json.dumps(realism)

    @staticmethod
    def vars_for_template(player):
        return dict(posts=json.loads(player.realism_posts_json or '[]'))

    @staticmethod
    def js_vars(player):
        return dict(posts=json.loads(player.realism_posts_json or '[]'))


class D_ClosingQuestions(Page):
    form_model  = 'player'
    form_fields = ['film_familiarity', 'task_difficulty', 'open_feedback']


class E_Debrief(Page):
    @staticmethod
    def vars_for_template(player):
        player.participant.finished = True
        return dict(
            redirect_url=player.session.prolific_completion_url,
            failed=player.failed_attention,
        )


def custom_export(players):
    yield [
        'session_code', 'participant_code', 'prolific_pid',
        'attn_civil_rating', 'attn_toxic_rating', 'failed_attention',
        'film_familiarity', 'task_difficulty', 'open_feedback',
        'doc_id', 'display_position', 'human_rating', 'realism_rating',
        'perspective_toxicity', 'gpt_toxicity',
    ]
    for player in players:
        order   = json.loads(player.post_order_json  or '[]')
        ratings = json.loads(player.ratings_json     or '{}')
        realism = json.loads(player.realism_json     or '{}')
        for i, post in enumerate(order):
            doc_id = str(post['doc_id'])
            yield [
                player.session.code,
                player.participant.code,
                player.prolific_pid,
                player.attn_civil_rating,
                player.attn_toxic_rating,
                player.failed_attention,
                player.film_familiarity,
                player.task_difficulty,
                player.open_feedback,
                doc_id,
                i + 1,
                ratings.get(doc_id),
                realism.get(doc_id),
                post.get('toxicity'),
                post.get('gpt_toxicity'),
            ]


page_sequence = [A_Intro, A2_Examples, B_Rating, C_Realism, D_ClosingQuestions, E_Debrief]
