from rlcard.envs.env import Env


class BigTwoGameSimplifiedEnv(Env):
    def _extract_state(self, state):
        return super()._extract_state(state)

    def _decode_action(self, action_id):
        return super()._decode_action(action_id)

    def get_payoffs(self):
        return super().get_payoffs()
