from otree.api import *
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield SubmissionMustFail(DInstructions, dict(q1A=0, q1B=1))
        yield DInstructions, dict(q1A=1, q1B=1)
        yield VideoInstructions
        yield SubmissionMustFail(Beliefs, dict(belief_others_charity=101, belief_others_alt=40,
                                               belief_self_charity=50, belief_self_alt=30))
        yield Beliefs, dict(belief_others_charity=60, belief_others_alt=40,
                            belief_self_charity=50, belief_self_alt=30)
        yield SubmissionMustFail(TimingInstructions, dict(comp_q1=1, comp_q2=4, comp_wrong=0))
        yield TimingInstructions, dict(comp_q1=3, comp_q2=4, comp_wrong=1)
        yield TimingDecision_MPL, {f'choice_{k}': (1 if k <= 4 else 2) for k in range(1, 12)}
        yield WTP, dict(pref_order=2, wtp_amount=0.3, wtp_why='test')
        yield Results
        assert self.player.participant.vars['belief_others_charity'] == 60
        assert self.player.rand in [1, 2]
