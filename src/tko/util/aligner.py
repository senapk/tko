from __future__ import annotations
from tko.util.rt import RT
from tko.util.rbuffer import RBuffer

class Aligner:
    @staticmethod
    def distribute_with_filler(left: RT, center: RT, right: RT, filler: str, frame_dx: int) -> RT:
        delta = frame_dx - len(center)
        left_pad, right_pad = 1, 1
        if delta > 0:
            delta_left = delta // 2
            left_pad  = max(1, delta_left - len(left))
            right_pad = max(1, (delta - delta_left) - len(right))
        return RBuffer().add(left).add(filler * left_pad).add(center).add(filler * right_pad).add(right).to_rt()