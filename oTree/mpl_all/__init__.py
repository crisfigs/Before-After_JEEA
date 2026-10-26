from otree.api import *
import random

doc = """
Page order: DInstructions (Part 2 instructions 1/2: options A/B, 2/2: videos and orders, then one comprehension check)
-> Beliefs -> TimingInstructions (Instructions 2/2 + comprehension) -> TimingDecision_MPL -> WTP -> Results.

Price list for video order (oTree 5).
11 rows: Option 1 = AltEmot (+ bonus in rows 1-5), Option 2 = EmotAlt (+ bonus in rows 7-11).
Row 6 is the zero-bonus row. One row is drawn and implemented:
rows 1 and 11 each with prob 27.5%, rows 2-10 share the remaining 45% equally (5% each).
Single switching (1 -> 2) is enforced in the browser and checked on the server.
Comprehension questions must be answered correctly before the decision page.
"""


class C(BaseConstants):
    NAME_IN_URL = 'mpl'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    NUM_ROWS = 11

    # Video files (mp4). Replace with your own links (the same ones you used as link1 / link2).
    CHARITY_VIDEO = "https://www.dropbox.com/s/hoh8zehqd960dmq/mostshocking2day.mp4?raw=1"
    ALT_VIDEO = "https://www.dropbox.com/s/iebfy6fzuewtk34/grass.mp4?raw=1"


    # Labels shown to participants. Choices are stored as 1 (Option 1 = 'AltEmot') and 2 (Option 2 = 'EmotAlt').
    LABEL_1 = 'Alternative video first'
    LABEL_2 = 'Charity video first'
    ORDER_1 = 'the Alternative Video first and the Charity Video after your choice between Option A and Option B'
    ORDER_2 = 'the Charity Video first and the Alternative Video after your choice between Option A and Option B'

    # Bonus in £ for each row (row 1 first)
    BONUS_1 = [1.00, 0.70, 0.50, 0.30, 0.10, 0, 0, 0, 0, 0, 0]
    BONUS_2 = [0, 0, 0, 0, 0, 0, 0.10, 0.30, 0.50, 0.70, 1.00]

    # Beliefs about others: paid if the guess is within BELIEF_TOL of the realized number (per 100)
    BELIEF_PRIZE = 0.10  # £ per correct guess (10 pence)
    BELIEF_TOL = 10  # +/- tolerance, in participants out of 100

    # Selection probabilities: 55% split over rows 1 and 11, 45% split over the rest
    PROB_EXTREME = 0.55 / 2                 # 27.5% each
    PROB_MIDDLE = 0.45 / (NUM_ROWS - 2)     # 5% each
    ROW_WEIGHTS = [PROB_EXTREME] + [PROB_MIDDLE] * (NUM_ROWS - 2) + [PROB_EXTREME]

    # Comprehension example table: Option 1 in rows 1-3, Option 2 in rows 4-11.
    COMP_SWITCH = 3     # number of rows with Option 1
    COMP1_ROW = 3       # question 1: Option 1 chosen, bonus £0.50
    COMP2_ROW = 5       # question 2: Option 2 chosen, no bonus (the £0.10 belongs to Option 1)

    # Exit survey: two rows of the price list repeated, to check the reliability of the switching point
    # Repeated price-list rows (C.REP_ROWS), stored as 1 = Option 1, 2 = Option 2
    REP_ROWS = [4, 8]  # repeated rows: Alternative first + £0.30, and Charity first + £0.30
    ZERO_ROW = 6  # row where neither order comes with a bonus (used on the Reasons page)

# Comprehension question texts (built from the constants, so they update if you change them)
def money(x):
    return f"£{x:.2f}"


# Part 2 comprehension: correct answers for q1A, q1B, q2_when, q3_avoid, q4_videos
Q1A_CORRECT = 1   # (me: 5, charity: 0)
Q1B_CORRECT = 1   # (me: 1, charity: 8)
Q2_CORRECT = 2    # the A/B choice is made in between the two videos
Q3_CORRECT = 2    # both videos are always watched; only the order is chosen
Q4_CORRECT = 1    #True
COMP_CHOICES_TABLE = [1] * C.COMP_SWITCH + [2] * (C.NUM_ROWS - C.COMP_SWITCH)

# Answer texts for the two orders: first video, A/B decision, second video
ALT_FIRST = "Watches Alternative Video → makes A/B decision → watches Charity Video"
CHARITY_FIRST = "Watches Charity Video → makes A/B decision → watches Alternative Video"

# Question 1: decision 3 -> Option 1 was chosen, bonus £0.50
COMP1_BONUS = money(C.BONUS_1[C.COMP1_ROW - 1])
COMP1_LABEL = (f"Suppose the computer randomly selects decision {C.COMP1_ROW}. "
               f"What happens for this person?")
COMP1_CHOICES = [
    [1, f"{CHARITY_FIRST}; bonus {COMP1_BONUS}"],
    [2, f"{ALT_FIRST}; bonus £0.00"],
    [3, f"{ALT_FIRST}; bonus {COMP1_BONUS}"],      # correct
    [4, f"{CHARITY_FIRST}; bonus £0.00"],
]
COMP1_CORRECT = 3

# Question 2: decision 5 -> Option 2 was chosen; the £0.10 in that row belongs to Option 1, so no bonus
COMP2_TRAP = money(C.BONUS_1[C.COMP2_ROW - 1])
COMP2_LABEL = (f"Suppose instead that the computer randomly selects decision {C.COMP2_ROW}. "
               f"What happens for this person?")
COMP2_CHOICES = [
    [1, f"{CHARITY_FIRST}; bonus {COMP2_TRAP}"],
    [2, f"{ALT_FIRST}; bonus {COMP2_TRAP}"],
    [3, f"{ALT_FIRST}; bonus £0.00"],
    [4, f"{CHARITY_FIRST}; bonus £0.00"],          # correct
]
COMP2_CORRECT = 4


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

def make_field3(label):
    return models.IntegerField(
        choices=[
            [0, 'False'],
            [1, 'True']],
        label=label,
        widget=widgets.RadioSelect,
    )
def make_choice():
    return models.IntegerField(choices=[1, 2], widget=widgets.RadioSelect)   # 1 = Option 1, 2 = Option 2

def make_emotion(label):
    return models.IntegerField(label=label, choices=[1, 2, 3, 4, 5], widget=widgets.RadioSelectHorizontal)


def make_slider(label):
    # blank=True so the page can give its own message if a slider was not touched (see slider_error)
    return models.IntegerField(label=label, min=0, max=100, blank=True)

class Player(BasePlayer):
    # Part 2 comprehension questions
    q1A = models.IntegerField(label="1. Option A pays: ", choices=[[0, '(me: 0, charity: 5)'], [1, '(me: 5, charity: 0)'], [2, '(me: 1, charity: 4)'], [3, '(me: 1, charity: 8)'], [4, '(me: 4, charity: 0)']])
    q1B = models.IntegerField(label="2. Option B pays: ", choices=[[0, '(me: 0, charity: 8)'], [1, '(me: 1, charity: 8)'], [2, '(me: 0, charity: 5)'], [3, '(me: 4, charity: 0)'], [4, '(me: 1, charity: 4)']])
    q2_when = models.IntegerField(
        label="3. When do you make your choice between Option A and Option B?",
        choices=[[1, 'Before watching either video'],
                 [2, 'In between the two videos'],
                 [3, 'After watching both videos']],
    )
    q3_avoid = models.IntegerField(
        label="4. Can you avoid watching either of the two videos?",
        choices=[[1, 'Yes, the second video is skipped once I have made my choice between Option A and Option B'],
                 [2, 'No, you watch both videos in any case; you only decide which one you watch first']],
    )
    q4_videos = models.IntegerField(
        label="5. True or false: the Charity Video is an emotional video related to the charity, "
              "while the Alternative Video is of similar length but unrelated to the charity.",
        choices=[[1, 'True'], [0, 'False']],
    )
    rand = models.IntegerField()   # 1 or 2, drawn 50/50 after the Part 2 page

    # Beliefs (asked after the video descriptions, before any video)
    # Question text shown to participants is written in Beliefs.html (so parts can be bold); labels here are for the data
    # (a) about others, out of 100; incentivized against the realized rates in this study
    belief_others_charity = models.IntegerField(
        min=0, max=100,
        label="Of 100 participants who watch the Charity Video first, how many do you think will donate (choose Option B)?",
    )
    belief_others_alt = models.IntegerField(
        min=0, max=100,
        label="Of 100 participants who watch the Alternative Video first, how many do you think will donate (choose Option B)?",
    )
    # (b) about oneself, 0-100 likelihood; not incentivized
    belief_self_charity = models.IntegerField(
        min=0, max=100,
        label="If you watch the Charity Video first, how likely is it that you will donate (choose Option B)? "
              "(0 = certainly not, 100 = certainly)",
    )
    belief_self_alt = models.IntegerField(
        min=0, max=100,
        label="If you watch the Alternative Video first, how likely is it that you will donate (choose Option B)? "
              "(0 = certainly not, 100 = certainly)",
    )

    # MPL comprehension
    #  answers as a dropdown menu per default
    comp_q1 = models.IntegerField(label=COMP1_LABEL, choices=COMP1_CHOICES)
    comp_q2 = models.IntegerField(label=COMP2_LABEL, choices=COMP2_CHOICES)
    comp_wrong = models.IntegerField(initial=0)  # number of failed attempts before passing

    # One field per row
    choice_1 = make_choice()
    choice_2 = make_choice()
    choice_3 = make_choice()
    choice_4 = make_choice()
    choice_5 = make_choice()
    choice_6 = make_choice()
    choice_7 = make_choice()
    choice_8 = make_choice()
    choice_9 = make_choice()
    choice_10 = make_choice()
    choice_11 = make_choice()

    # Summary measures
    num_opt1 = models.IntegerField()     # number of rows where Option 1 (AltEmot) was chosen
    switch_row = models.IntegerField()   # first row where Option 2 (EmotAlt) was chosen; empty if never

    # Implemented row
    paid_row = models.IntegerField()     # row drawn at random
    paid_option = models.IntegerField()  # 1 or 2: option chosen in that row
    imp_order = models.StringField()  # 'AltEmot' or 'EmotAlt': order implemented
    bonus = models.FloatField()          # bonus in £ from the drawn row

    # Unincentivised WTP question (asked after the decisions, before the result is shown)
    pref_order = models.IntegerField(
        label="Which order would you prefer?",
        choices=[[1, 'Alternative video first'], [2, 'Charity video first'], [0, 'I have no preference']],
        widget=widgets.RadioSelect,
    )
    wtp_amount = models.FloatField(
        label="What is the largest bonus (in £) you would be willing to give up "
              "to watch the videos in your preferred order? (Enter 0 if you have no preference.)",
        min=0,
    )

    # Choice between Option A and Option B (made in between the two videos)
    task1 = models.StringField(choices=['A', 'B'])   # 'A' = keep £5; 'B' = keep £1, £8 to Save the Children
    time_choice = models.IntegerField(blank=True)     # seconds spent on the choice page

    # Attention questions, Charity Video (1 = correct answer, so the sum of the three is the number correct)
    controlq1 = make_field3(label="...a girl blowing some candles.")
    controlq2 = make_field3(label="...a gas mask.")
    controlq3 = models.IntegerField(
        choices=[[1, 'False'], [0, 'True']],
        label="...a girl on an airplane.",
        widget=widgets.RadioSelect)
    # Attention questions, Alternative Video
    controlq_presenter = make_field3(label="...a male presenter.")
    controlq_drawing = make_field3(label="...a drawing.")
    controlq_woman = models.IntegerField(
        choices=[[1, 'False'], [0, 'True']],
        label="...a woman.",
        widget=widgets.RadioSelect)

    sum_correct_charity = models.IntegerField()   # 0-3 correct, Charity Video questions
    sum_correct_alt = models.IntegerField()       # 0-3 correct, Alternative Video questions
    number = models.IntegerField()                # 1 with prob 1%: failing the check only screens out if this is 1

   # Feedback
    q_feedback = models.LongStringField(label="Do you have any comments about this study?", blank=True)
    q_feedback_pilot = models.LongStringField(label="Was anything in the instructions unclear or confusing?", blank=True)

    # Payment
    payment_number = models.IntegerField()   # 1 with prob 20%: the Option A/B choice is paid out
    payment = models.FloatField()            # £ from the Option A/B choice: 5 (A) or 1 (B) if selected, else 0
    donation = models.FloatField()           # £ to Save the Children: 8 if selected and B, else 0
    total_payment = models.FloatField()      # payment + bonus from the selected row of the decision table
                                             # (the guessing bonus is added after the study)

    # ---- Exit survey ----
    # Question texts are written in the templates (so parts can be bold); labels here are for the data
    # Experienced emotions, Charity Video (1 = very weak, 5 = very high)
    happy_charity = make_emotion("Happiness")
    sad_charity = make_emotion("Sadness")
    fear_charity = make_emotion("Fear")
    disgust_charity = make_emotion("Disgust")
    anger_charity = make_emotion("Anger")
    compassion_charity = make_emotion("Compassion")
    guilt_charity = make_emotion("Guilt")
    boredom_charity = make_emotion("Boredom")
    # Experienced emotions, Alternative Video
    happy_alt = make_emotion("Happiness")
    sad_alt = make_emotion("Sadness")
    fear_alt = make_emotion("Fear")
    disgust_alt = make_emotion("Disgust")
    anger_alt = make_emotion("Anger")
    compassion_alt = make_emotion("Compassion")
    guilt_alt = make_emotion("Guilt")
    boredom_alt = make_emotion("Boredom")

    # Anticipated emotions (0 = not at all, 100 = very much)
    ant_charity = make_slider("Anticipated the emotions, Charity Video")
    ant_alt = make_slider("Anticipated the emotions, Alternative Video")

    # Temptation, per video (0 = not at all, 100 = very much)
    tempt_donate_charity = make_slider("Tempted to donate while watching the Charity Video")
    tempt_keep_charity = make_slider("Tempted to keep while watching the Charity Video")
    ant_tempt_donate_charity = make_slider("Expected to be tempted to donate, Charity Video")
    ant_tempt_keep_charity = make_slider("Expected to be tempted to keep, Charity Video")
    tempt_donate_alt = make_slider("Tempted to donate while watching the Alternative Video")
    tempt_keep_alt = make_slider("Tempted to keep while watching the Alternative Video")
    ant_tempt_donate_alt = make_slider("Expected to be tempted to donate, Alternative Video")
    ant_tempt_keep_alt = make_slider("Expected to be tempted to keep, Alternative Video")

    # Counterfactual: A/B choice had the implemented order been reversed
    cf_choice = models.StringField(
        choices=[['A', 'Option A (you: £5, charity: £0)'], ['B', 'Option B (you: £1, charity: £8)']],
        widget=widgets.RadioSelect, label="")
    # Why they prefer the order chosen in the zero-bonus row (C.ZERO_ROW)
    reason_order = models.LongStringField(label="")

    # Repeated price-list rows (C.REP_ROWS), stored as 1 = Option 1, 2 = Option 2
    rep_choice_a = make_choice()
    rep_choice_b = make_choice()
    rep_match = models.IntegerField()  # 0-2: number of repeated rows answered as in the original table

# FUNCTIONS

# Text shown in one cell of the table, e.g. "Alternative video first + £0.70"
# (no "+ £..." when the bonus is 0). Used only inside get_rows().
def option_text(label, bonus):
    if bonus > 0:
        return f"{label} + £{bonus:.2f}"
    return label


# Builds the content of the 11 table rows (decision number, field name, text of Option 1 and Option 2).
# Used by the TimingDecision_MPL page (table with active buttons) and, through example_rows(),
# by the example tables on the TimingInstructions page (Instructions 2/2 and comprehension screens).
def get_rows():
    rows = []
    for k in range(1, C.NUM_ROWS + 1):
        rows.append(dict(
            number=k,
            field='choice_' + str(k),
            option_1=option_text(C.LABEL_1, C.BONUS_1[k - 1]),
            option_2=option_text(C.LABEL_2, C.BONUS_2[k - 1]),
        ))
    return rows


# Rows for the example tables (TimingInstructions page): same text as get_rows(), plus which
# button is shown as ticked (choices: 1, 2 or None per row) and which rows are highlighted.
def example_rows(choices, highlight_rows):
    rows = get_rows()
    for row, ch in zip(rows, choices):
        row['opt1_checked'] = (ch == 1)
        row['opt2_checked'] = (ch == 2)
        row['highlight'] = (row['number'] in highlight_rows)
    return rows


# Checks that all 1's come before all 2's (all-1 and all-2 are allowed).
# Used in TimingDecision_MPL.error_message as a server-side backup: the page's JavaScript already
# enforces single switching, this only catches cases where the JavaScript did not run.
def is_single_switch(choices):
    n_1 = choices.count(1)
    return choices == [1] * n_1 + [2] * (C.NUM_ROWS - n_1)


# PAGES

# Variables for the Instructions 2/2 text and example table.
def instructions2_vars():
    # Example table: Option 1 in rows 1-4, Option 2 in rows 5-11; row 9 is the "randomly selected" one
    ex_row = 9
    choices = [1] * 4 + [2] * (C.NUM_ROWS - 4)

    return dict(
        table=example_rows(choices, [ex_row]),
        ex_row=ex_row,
        ex_bonus=money(C.BONUS_2[ex_row - 1]),     # £0.50
        prob_extreme=f"{C.PROB_EXTREME * 100:g}%",  # 27.5%
        prob_middle=f"{C.PROB_MIDDLE * 100:g}%",    # 5%
    )


# Part 2 on one page with three screens: Instructions 1/2 (options A/B), Instructions 2/2 (videos and orders),
# comprehension check (A/B payoffs + videos and timing). Back/Next between screens happen in the browser.
class DInstructions(Page):
    form_model = 'player'
    form_fields = ['q1A', 'q1B', 'q2_when', 'q3_avoid', 'q4_videos']
    @staticmethod
    def error_message(player: Player, values):
        if (values['q1A'] != Q1A_CORRECT or values['q1B'] != Q1B_CORRECT
                or values['q2_when'] != Q2_CORRECT or values['q3_avoid'] != Q3_CORRECT
                or values['q4_videos'] != Q4_CORRECT):
            return 'You did not answer all questions correctly. Please go back to the instructions and revise your answers.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.rand = random.choice([1, 2])   # 50/50


# Beliefs about others (incentivized) and about oneself (not incentivized), before any video.
class Beliefs(Page):
    form_model = 'player'
    form_fields = ['belief_others_charity', 'belief_others_alt', 'belief_self_charity', 'belief_self_alt']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(belief_pence=round(C.BELIEF_PRIZE * 100))   # e.g. 10 (pence)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Belief payment is computed after the study, once the realized rates are known
        for f in Beliefs.form_fields:
            player.participant.vars[f] = getattr(player, f)

# One oTree page with two screens (Instructions 2/2, Comprehension check).
# Back/Next between the screens happen in the browser; the page is only submitted
# from the comprehension screen, and only when both answers are correct.
class TimingInstructions(Page):
    form_model = 'player'
    form_fields = ['comp_q1', 'comp_q2', 'comp_wrong']

    @staticmethod
    def vars_for_template(player: Player):
        v = instructions2_vars()                                  # Instructions 2/2 example table
        v['comp_table'] = example_rows(COMP_CHOICES_TABLE, [])   # comprehension table, no highlighted row
        return v

    @staticmethod
    def js_vars(player: Player):
        return dict(correct_q1=COMP1_CORRECT, correct_q2=COMP2_CORRECT)

    @staticmethod
    def error_message(player: Player, values):
        # Backup check; the page's JavaScript already shows the red alert
        if values['comp_q1'] != COMP1_CORRECT or values['comp_q2'] != COMP2_CORRECT:
            return 'At least one answer is not correct. Please try again.'


class TimingDecision_MPL(Page):
    form_model = 'player'
    form_fields = ['choice_' + str(k) for k in range(1, C.NUM_ROWS + 1)]

    @staticmethod
    def vars_for_template(player: Player):
        return dict(rows=get_rows())

    @staticmethod
    def error_message(player: Player, values):
        # Backup check; the page's JavaScript already enforces this
        choices = [values['choice_' + str(k)] for k in range(1, C.NUM_ROWS + 1)]
        if not is_single_switch(choices):
            return 'Please switch from Option 1 to Option 2 at most once.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        choices = [getattr(player, 'choice_' + str(k)) for k in range(1, C.NUM_ROWS + 1)]

        # Summary measures
        player.num_opt1 = choices.count(1)
        if 2 in choices:
            player.switch_row = choices.index(2) + 1

        # Draw one row (rows 1 and 11 more likely) and implement the choice made in it
        player.paid_row = random.choices(range(1, C.NUM_ROWS + 1), weights=C.ROW_WEIGHTS)[0]
        player.paid_option = choices[player.paid_row - 1]
        if player.paid_option == 1:
            player.imp_order = 'AltEmot'
            player.bonus = C.BONUS_1[player.paid_row - 1]
        else:
            player.imp_order = 'EmotAlt'
            player.bonus = C.BONUS_2[player.paid_row - 1]

        # Store for later apps
        player.participant.vars['imp_order'] = player.imp_order
        player.participant.vars['mpl_bonus'] = player.bonus

class WTP(Page):
    form_model = 'player'
    form_fields = ['pref_order', 'wtp_amount']

    @staticmethod
    def error_message(player: Player, values):
        # The amount is only needed if the person has a preferred order
        if values['pref_order'] in [1, 2] and values['wtp_amount'] is None:
            return 'Please enter the largest bonus you would be willing to give up.'

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # No preference -> no amount stored
        if player.pref_order == 0:
            player.wtp_amount = None

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        if player.paid_option == 1:
            label = C.LABEL_1
            order = C.ORDER_1
        else:
            label = C.LABEL_2
            order = C.ORDER_2

        # The participant's own selected row, with their choice ticked (same text as the decision table)
        choices = [getattr(player, 'choice_' + str(k)) for k in range(1, C.NUM_ROWS + 1)]
        selected_row = example_rows(choices, [player.paid_row])[player.paid_row - 1]

        return dict(received=label, order=order, bonus_text=money(player.bonus), selected_row=selected_row)

def charity_first(player: Player):
    return player.imp_order == 'EmotAlt'


def video_number_is_charity(player: Player, k):
    # k = 1 (first video) or 2 (second video); True if that video is the Charity Video
    return charity_first(player) if k == 1 else not charity_first(player)


CHARITY_QUESTIONS = ['controlq1', 'controlq2', 'controlq3']
ALT_QUESTIONS = ['controlq_presenter', 'controlq_drawing', 'controlq_woman']


def video_vars(player: Player, k):
    if video_number_is_charity(player, k):
        return dict(video_link=C.CHARITY_VIDEO)
    return dict(video_link=C.ALT_VIDEO)


def failed(player: Player):
    # Failed = at most 2 of the 3 questions right for either video (and the 1% draw is 1)
    return (player.sum_correct_charity <= 2 or player.sum_correct_alt <= 2) and player.number == 1


def failed_vars(player: Player):
    error_code = player.session.config.get('error_code', '')
    return dict(errorlink="https://app.prolific.co/submissions/complete?cc=" + str(error_code))


# Alert shown before each video (same template for both)
class VideoAlert1(Page):
    template_name = 'mpl_all/VideoAlert.html'


class VideoAlert2(Page):
    template_name = 'mpl_all/VideoAlert.html'


# The videos (same template for both; which file is shown depends on the implemented order)
class Video1(Page):
    template_name = 'mpl_all/Video.html'

    @staticmethod
    def vars_for_template(player: Player):
        return video_vars(player, 1)


class Video2(Page):
    template_name = 'mpl_all/Video.html'

    @staticmethod
    def vars_for_template(player: Player):
        return video_vars(player, 2)


# Choice between Option A and Option B, in between the two videos
class OptionChoice(Page):
    form_model = 'player'
    form_fields = ['task1', 'time_choice']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['task1'] = player.task1


# Attention questions about both videos, on one page after the second video.
# The questions are grouped by video, in the order the participant watched them.
class Attention(Page):
    form_model = 'player'
    form_fields = CHARITY_QUESTIONS + ALT_QUESTIONS

    @staticmethod
    def vars_for_template(player: Player):
        return dict(charity_first=charity_first(player))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.sum_correct_charity = sum(getattr(player, f) for f in CHARITY_QUESTIONS)
        player.sum_correct_alt = sum(getattr(player, f) for f in ALT_QUESTIONS)
        player.number = random.choices([1, 0], weights=(1, 99), k=1)[0]


# Screen-out page (link back to Prolific with the error code); shown only if the check is failed
# if the participant got one question wrong in either video, with 1% prob its screened out
class FailedAttention(Page):
    @staticmethod
    def is_displayed(player: Player):
        return failed(player)

    @staticmethod
    def vars_for_template(player: Player):
        return failed_vars(player)

# ---- Exit survey pages ----

EMOTIONS = ['happy', 'sad', 'fear', 'disgust', 'anger', 'compassion', 'guilt', 'boredom']

EMOTION_LABELS = {'happy': 'Happiness', 'sad': 'Sadness', 'fear': 'Fear', 'disgust': 'Disgust',
                  'anger': 'Anger', 'compassion': 'Compassion', 'guilt': 'Guilt', 'boredom': 'Boredom'}

def video_name(player: Player, k):
    return 'Charity Video' if video_number_is_charity(player, k) else 'Alternative Video'


def video_suffix(player: Player, k):
    return '_charity' if video_number_is_charity(player, k) else '_alt'


def emotion_order(player: Player):
    # Random order of the emotions, drawn once per participant and kept the same for both videos
    if 'emo_order' not in player.participant.vars:
        order = EMOTIONS.copy()
        random.shuffle(order)
        player.participant.vars['emo_order'] = order
    return player.participant.vars['emo_order']


def slider_error(values, fields):
    # Server-side backup; slider.js already blocks submitting with an empty slider
    for f in fields:
        if values[f] is None:
            return 'Please answer every question by clicking on the scale.'


def emotion_fields(player: Player, k):
    s = video_suffix(player, k)
    return [e + s for e in emotion_order(player)] + ['ant' + s]


def emotion_vars(player: Player, k, position):
    return dict(video_name=video_name(player, k), position=position,
                ant_field='ant' + video_suffix(player, k))


# Rows of the emotion table and the anticipation slider for video k (1 = first watched, 2 = second)
def emotion_block(player: Player, k, position):
    s = video_suffix(player, k)
    rows = [dict(field=e + s, label=EMOTION_LABELS[e]) for e in emotion_order(player)]
    return dict(name=video_name(player, k), position=position, rows=rows, ant='ant' + s)


# Experienced and anticipated emotions for both videos on one page (in the order watched)
class Emotions(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return emotion_fields(player, 1) + emotion_fields(player, 2)

    @staticmethod
    def vars_for_template(player: Player):
        return dict(videos=[emotion_block(player, 1, 'first'), emotion_block(player, 2, 'second')])

    @staticmethod
    def error_message(player: Player, values):
        return slider_error(values, ['ant' + video_suffix(player, 1), 'ant' + video_suffix(player, 2)])

# Experienced and anticipated temptation to donate and to keep, one block per video (in the order watched)
def temptation_fields(player: Player):
    fields = []
    for k in [1, 2]:
        s = video_suffix(player, k)
        fields += ['tempt_donate' + s, 'tempt_keep' + s, 'ant_tempt_donate' + s, 'ant_tempt_keep' + s]
    return fields


class Temptation(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return temptation_fields(player)

    @staticmethod
    def vars_for_template(player: Player):
        videos = []
        for k, position in [(1, 'first'), (2, 'second')]:
            s = video_suffix(player, k)
            videos.append(dict(
                name=video_name(player, k),
                position=position,
                donate='tempt_donate' + s,
                keep='tempt_keep' + s,
                ant_donate='ant_tempt_donate' + s,
                ant_keep='ant_tempt_keep' + s,
            ))
        return dict(videos=videos)

    @staticmethod
    def error_message(player: Player, values):
        return slider_error(values, temptation_fields(player))


# Counterfactual (relative to the implemented order) and reason for the preferred order (zero-bonus row)
class Reasons(Page):
    form_model = 'player'
    form_fields = ['cf_choice', 'reason_order']

    @staticmethod
    def vars_for_template(player: Player):
        if getattr(player, 'choice_' + str(C.ZERO_ROW)) == 2:
            pref_first = 'Charity Video'
        else:
            pref_first = 'Alternative Video'
        return dict(first=video_name(player, 1), second=video_name(player, 2), pref_first=pref_first)


# Two rows of the price list again
class RepeatRows(Page):
    form_model = 'player'
    form_fields = ['rep_choice_a', 'rep_choice_b']

    @staticmethod
    def vars_for_template(player: Player):
        rows = get_rows()
        rep = [rows[C.REP_ROWS[0] - 1], rows[C.REP_ROWS[1] - 1]]
        rep[0]['field'] = 'rep_choice_a'
        rep[1]['field'] = 'rep_choice_b'
        return dict(rep_rows=rep)

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        original_a = getattr(player, 'choice_' + str(C.REP_ROWS[0]))
        original_b = getattr(player, 'choice_' + str(C.REP_ROWS[1]))
        player.rep_match = int(player.rep_choice_a == original_a) + int(player.rep_choice_b == original_b)

# Feedback questions; the payment is computed here so that it is fixed before the Back page is shown
class Feedback(Page):
    form_model = 'player'
    form_fields = ['q_feedback', 'q_feedback_pilot']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.payment_number = random.choices([1, 0], weights=(20, 80), k=1)[0]   # 1 in 5
        if player.payment_number == 1 and player.task1 == 'A':
            player.payment = 5
            player.donation = 0
        elif player.payment_number == 1 and player.task1 == 'B':
            player.payment = 1
            player.donation = 8
        else:
            player.payment = 0
            player.donation = 0
        # The total payment without including the incentivized beliefs
        player.total_payment = player.payment + player.bonus


# Payment summary and the link back to Prolific (no Next button)
class Back(Page):
    @staticmethod
    def js_vars(player: Player):
        cc_code = player.session.config.get('cc_code', '')
        return dict(completionlink="https://app.prolific.co/submissions/complete?cc=" + str(cc_code))

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            payment_text=money(player.payment),
            bonus_text=money(player.bonus),
            total_text=money(player.total_payment),
            has_bonus=player.bonus > 0,
            belief_pence=round(C.BELIEF_PRIZE * 100),
        )


page_sequence = [
    DInstructions,
    Beliefs,
    TimingInstructions,
    #Order choice
    TimingDecision_MPL,
    WTP,
    Results,
    VideoAlert1,
    Video1,
    #Donation Choice
    OptionChoice,
    VideoAlert2,
    Video2,
    Attention,
    FailedAttention,
    #Final Survey
    Emotions,
    Temptation,
    Reasons,
    RepeatRows,
    Feedback,
    Back
]