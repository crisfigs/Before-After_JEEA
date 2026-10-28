from otree.api import *
from . import *


class PlayerBot(Bot):
    # Case 'alt_first': the bot chooses "Alternative video first" in every row.
    # Case 'charity_first': the bot chooses "Charity video first" in every row.
    # Which column (Option 1 or 2) that is depends on the randomized mpl_option1.
    cases = ['alt_first', 'charity_first']

    def play_round(self):
        # Part 2 instructions + comprehension
        yield SubmissionMustFail(DInstructions, dict(q1A=0, q1B=1, q2_when=2, q3_avoid=2, q4_videos=1))
        yield DInstructions, dict(q1A=1, q1B=1, q2_when=2, q3_avoid=2, q4_videos=1)

        # Beliefs
        yield SubmissionMustFail(Beliefs, dict(belief_others_charity=101, belief_others_alt=40,
                                               belief_self_charity=50, belief_self_alt=30))
        yield Beliefs, dict(belief_others_charity=60, belief_others_alt=40,
                            belief_self_charity=50, belief_self_alt=30)

        # Layout of the decision table, drawn in creating_session
        assert self.player.mpl_option1 in ['AltEmot', 'EmotAlt']

        # Comprehension questions: the correct answers depend on the layout
        ok1 = comp1_correct(self.player)
        ok2 = comp2_correct(self.player)
        yield SubmissionMustFail(TimingInstructions, dict(comp_q1=2, comp_q2=ok2, comp_wrong=0))   # 2 is never correct
        yield TimingInstructions, dict(comp_q1=ok1, comp_q2=ok2, comp_wrong=1)

        # Decision table: tick the column that holds the order of this case
        if self.case == 'alt_first':
            opt = 1 if alt_is_opt1(self.player) else 2
        else:
            opt = 2 if alt_is_opt1(self.player) else 1
        yield TimingDecision_MPL, {f'choice_{k}': opt for k in range(1, C.NUM_ROWS + 1)}
        yield WTP, dict(pref_order=2, wtp_amount=0.3)
        yield Results

        # The implemented order must be the order the bot chose, whatever the layout
        expected = 'AltEmot' if self.case == 'alt_first' else 'EmotAlt'
        assert self.player.imp_order == expected

        # Correct answers to the attention questions
        charity_ok = dict(controlq1=1, controlq2=1, controlq3=1)
        alt_ok = dict(controlq_presenter=1, controlq_drawing=1, controlq_woman=1)

        # First video, choice, second video
        yield VideoAlert1
        yield Submission(Video1, check_html=False)   # the NEXT button only appears after the video in a real browser
        yield SubmissionMustFail(OptionChoice, dict(task1='C', time_choice=3))
        yield OptionChoice, dict(task1='B', time_choice=3)
        yield VideoAlert2
        yield Submission(Video2, check_html=False)

        # Attention questions about both videos (all correct, so FailedAttention is skipped)
        yield Attention, dict(**charity_ok, **alt_ok)

        # Exit survey (field names end in _charity / _alt; the pages show them in the order watched)
        emo = {f'{e}_{v}': 3 for e in EMOTIONS for v in ['charity', 'alt']}
        yield Emotions, dict(**emo, ant_charity=50, ant_alt=20)
        tempt = {f'{q}_{v}': 40 for q in ['tempt_donate', 'tempt_keep', 'ant_tempt_donate', 'ant_tempt_keep']
                 for v in ['charity', 'alt']}
        yield Temptation, tempt
        yield Reasons, dict(cf_choice='A', reason_order='no reason')

        yield Feedback, dict(q_feedback='fine', q_feedback_pilot='')
        # Back has no Next button (it links to Prolific), so the bot stops here

        assert self.player.task1 == 'B'
        expected_payment = 1 if self.player.payment_number == 1 else 0
        assert self.player.payment == expected_payment
        assert self.player.total_payment == expected_payment + self.player.bonus
        assert self.player.sum_correct_charity == 3 and self.player.sum_correct_alt == 3
        assert self.player.participant.vars['belief_others_charity'] == 60
