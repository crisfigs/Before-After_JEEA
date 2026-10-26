from otree.api import *
from . import *


class PlayerBot(Bot):
    # Case 'alt_first': Option 1 in every row -> Alternative Video first.
    # Case 'charity_first': Option 2 in every row -> Charity Video first.
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

        # Decision table
        yield SubmissionMustFail(TimingInstructions, dict(comp_q1=1, comp_q2=4, comp_wrong=0))
        yield TimingInstructions, dict(comp_q1=3, comp_q2=4, comp_wrong=1)
        opt = 1 if self.case == 'alt_first' else 2
        yield TimingDecision_MPL, {f'choice_{k}': opt for k in range(1, C.NUM_ROWS + 1)}
        yield WTP, dict(pref_order=2, wtp_amount=0.3)
        yield Results

        expected = 'AltEmot' if self.case == 'alt_first' else 'EmotAlt'
        assert self.player.news_type == expected

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

        yield Feedback, dict(q_feedback='fine', q_feedback_pilot='')
        # Back has no Next button (it links to Prolific), so the bot stops here

        assert self.player.task1 == 'B'
        expected_payment = 1 if self.player.payment_number == 1 else 0
        assert self.player.payment == expected_payment
        assert self.player.total_payment == expected_payment + self.player.bonus
        assert self.player.sum_correct_charity == 3 and self.player.sum_correct_alt == 3
        assert self.player.participant.vars['belief_others_charity'] == 60
        assert self.player.rand in [1, 2]