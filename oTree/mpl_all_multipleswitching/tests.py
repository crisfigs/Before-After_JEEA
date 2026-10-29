from otree.api import *
from oTree.mpl_all_multipleswitching.mpl_all import *


class PlayerBot(Bot):
    # Case 'alt_first': the bot chooses "Alternative video first" in every row.
    # Case 'charity_first': the bot chooses "Charity video first" in every row.
    # Case 'multi_switch': the bot alternates between Option 1 and Option 2 (1, 2, 1, 2, ...).
    # Which column (Option 1 or 2) holds which order depends on the randomized mpl_option1.
    cases = ['alt_first', 'charity_first', 'multi_switch']

    def play_round(self):
        # Part 2 instructions + comprehension
        yield SubmissionMustFail(DInstructions, dict(q1A=0, q1B=1, q2_when=2, q3_avoid=2, q4_videos=1))
        yield DInstructions, dict(q1A=1, q1B=1, q2_when=2, q3_avoid=2, q4_videos=1)

        # Beliefs (belief_self_*: 0 = Option A, 1 = Option B)
        yield SubmissionMustFail(Beliefs, dict(belief_others_charity=101, belief_others_alt=40,
                                               belief_self_charity=1, belief_self_alt=0, honeypot=''))
        yield Beliefs, dict(belief_others_charity=60, belief_others_alt=40,
                            belief_self_charity=1, belief_self_alt=0, honeypot='')

        # Layout of the decision table, drawn in creating_session
        assert self.player.mpl_option1 in ['AltEmot', 'EmotAlt']

        # Comprehension questions: the correct answers depend on the layout
        ok1 = comp1_correct(self.player)
        ok2 = comp2_correct(self.player)
        yield SubmissionMustFail(TimingInstructions, dict(comp_q1=2, comp_q2=ok2, comp_wrong=0))   # 2 is never correct
        yield TimingInstructions, dict(comp_q1=ok1, comp_q2=ok2, comp_wrong=1)

        # Decision table. The bot does not run JavaScript, so it fills in the two hidden fields itself
        if self.case == 'alt_first':
            opt = 1 if alt_is_opt1(self.player) else 2
            choices = {f'choice_{k}': opt for k in range(1, C.NUM_ROWS + 1)}
            warned = 0
        elif self.case == 'charity_first':
            opt = 2 if alt_is_opt1(self.player) else 1
            choices = {f'choice_{k}': opt for k in range(1, C.NUM_ROWS + 1)}
            warned = 0
        else:
            choices = {f'choice_{k}': (1 if k % 2 == 1 else 2) for k in range(1, C.NUM_ROWS + 1)}
            warned = 1
        yield TimingDecision_MPL, dict(**choices, mpl_warned=warned, mpl_first_try='')

        # Switching pattern
        if self.case == 'multi_switch':
            assert self.player.consistent is False
            assert self.player.num_switches == C.NUM_ROWS - 1
        else:
            assert self.player.consistent is True
            assert self.player.num_switches == 0

        yield WTP, dict(pref_order=2, wtp_amount=0.3)
        yield Results

        # The implemented order must be the order the bot chose, whatever the layout
        if self.case == 'alt_first':
            assert self.player.imp_order == 'AltEmot'
        elif self.case == 'charity_first':
            assert self.player.imp_order == 'EmotAlt'
        else:
            assert self.player.imp_order in ['AltEmot', 'EmotAlt']

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
        yield Emotions, emo
        yield Temptation, dict(tempt_donate_charity=40, ant_tempt_donate_charity=30,
                               tempt_donate_alt=10, ant_tempt_donate_alt=5)
        yield Reasons, dict(cf_choice='A', reason_order='no reason')
        yield Donation_behaviourq, dict(donationq=0, donationqother=1, charityq=4, knowstc=1)

        yield Feedback, dict(q_feedback='fine', q_feedback_pilot='')
        # Back has no Next button (it links to Prolific), so the bot stops here

        assert sorted(self.player.emo_order.split(',')) == sorted(EMOTIONS)
        assert self.player.task1 == 'B'
        expected_payment = 1 if self.player.payment_number == 1 else 0
        assert self.player.payment == expected_payment
        assert self.player.total_payment == expected_payment + self.player.bonus
        assert self.player.sum_correct_charity == 3 and self.player.sum_correct_alt == 3
        assert self.player.participant.vars['belief_others_charity'] == 60
