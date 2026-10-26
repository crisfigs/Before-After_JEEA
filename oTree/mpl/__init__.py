from otree.api import *
import random

doc = """
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

    # Labels shown to participants. Choices are stored as 1 (Option 1 = 'AltEmot') and 2 (Option 2 = 'EmotAlt').
    LABEL_1 = 'Alternative video first'
    LABEL_2 = 'Charity video first'
    ORDER_1 = 'the Alternative Video first and the Charity Video after your choice between Option A and Option B'
    ORDER_2 = 'the Charity Video first and the Alternative Video after your choice between Option A and Option B'

    # Bonus in £ for each row (row 1 first)
    BONUS_1 = [1.00, 0.70, 0.50, 0.30, 0.10, 0, 0, 0, 0, 0, 0]
    BONUS_2 = [0, 0, 0, 0, 0, 0, 0.10, 0.30, 0.50, 0.70, 1.00]

    # Selection probabilities: 55% split over rows 1 and 11, 45% split over the rest
    PROB_EXTREME = 0.55 / 2                 # 27.5% each
    PROB_MIDDLE = 0.45 / (NUM_ROWS - 2)     # 5% each
    ROW_WEIGHTS = [PROB_EXTREME] + [PROB_MIDDLE] * (NUM_ROWS - 2) + [PROB_EXTREME]

    # Comprehension example table: Option 1 in rows 1-3, Option 2 in rows 4-11.
    COMP_SWITCH = 3     # number of rows with Option 1
    COMP1_ROW = 3       # question 1: Option 1 chosen, bonus £0.50
    COMP2_ROW = 5       # question 2: Option 2 chosen, no bonus (the £0.10 belongs to Option 1)


# Comprehension question texts (built from the constants, so they update if you change them)
def money(x):
    return f"£{x:.2f}"


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


def make_choice():
    return models.IntegerField(choices=[1, 2], widget=widgets.RadioSelect)   # 1 = Option 1, 2 = Option 2


class Player(BasePlayer):
    # Comprehension
    # No widget given -> oTree shows the answers as a dropdown menu
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
    news_type = models.StringField()     # 'AltEmot' or 'EmotAlt' received
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
    wtp_why = models.LongStringField(
        label="[Not sure of this] Why do you prefer this order?",
        blank=True,
    )
# FUNCTIONS

# Text shown in one cell of the table, e.g. "Alternative video first + £0.70"
# (no "+ £..." when the bonus is 0). Used only inside get_rows().
def option_text(label, bonus):
    if bonus > 0:
        return f"{label} + £{bonus:.2f}"
    return label


# Builds the content of the 11 table rows (decision number, field name, text of Option 1 and Option 2).
# Used by the Decision page (table with active buttons) and, through example_rows(),
# by the example tables on the Instructions page (Instructions 2/2 and comprehension screens).
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


# Rows for the example tables (Instructions page): same text as get_rows(), plus which
# button is shown as ticked (choices: 1, 2 or None per row) and which rows are highlighted.
def example_rows(choices, highlight_rows):
    rows = get_rows()
    for row, ch in zip(rows, choices):
        row['opt1_checked'] = (ch == 1)
        row['opt2_checked'] = (ch == 2)
        row['highlight'] = (row['number'] in highlight_rows)
    return rows


# Checks that all 1's come before all 2's (all-1 and all-2 are allowed).
# Used in Decision.error_message as a server-side backup: the page's JavaScript already
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


# One oTree page with three screens (Instructions 1/2, Instructions 2/2, Comprehension check).
# Back/Next between the screens happen in the browser; the page is only submitted
# from the comprehension screen, and only when both answers are correct.
class Instructions(Page):
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


class Decision(Page):
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
            player.news_type = 'AltEmot'
            player.bonus = C.BONUS_1[player.paid_row - 1]
        else:
            player.news_type = 'EmotAlt'
            player.bonus = C.BONUS_2[player.paid_row - 1]

        # Store for later apps
        player.participant.vars['news_type'] = player.news_type
        player.participant.vars['mpl_bonus'] = player.bonus

class WTP(Page):
    form_model = 'player'
    form_fields = ['pref_order', 'wtp_amount', 'wtp_why']

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

page_sequence = [Instructions, Decision, WTP, Results]