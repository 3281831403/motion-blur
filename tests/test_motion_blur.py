import pytest

from render import motion_blur as mod

CASES = [
    ('sample_shutter', [0.016666666666666666, 180, 3], [0.0, 0.004166666666666667, 0.008333333333333333], True),
    ('sample_shutter', [0.016666666666666666, 0, 2], [0.0, 0.0], True),
    ('compose_motion_vector', [1, 2, 90, 2], [1, 2, 90, 1.0], True),
    ('depth_weight', [5, 0, 10], 0.5, True),
    ('depth_weight', [20, 0, 10], 0.0, True),
    ('split_layers', [[1.0, 0.5, 1.0, 0.2]], (2, 2), False),
    ('adaptive_sample_count', [4, 8294400], 36, False),
    ('clamp_shutter_angle', [400], 360.0, True),
    ('clamp_shutter_angle', [-10], 0.0, True),
    ('trim_history', [[1, 2, 3], 2], [2, 3], False),
    ('trim_history', [[1], 0], [], False),
    ('rolling_offset', [10, 100, 0.5], 0.05, True),
    ('particle_vector', [(0, 0), (2, 3)], [2, 3], False),
    ('order_postprocess', [['dof', 'motion_blur']], ['motion_blur', 'dof'], False),
    ('order_postprocess', [['taa', 'dof']], ['dof', 'taa'], False),
]


@pytest.mark.parametrize("func_name,args,expected,approx", CASES)
def test_motion_blur_contract(func_name, args, expected, approx):
    func = getattr(mod, func_name)
    result = func(*args)
    if approx:
        assert result == pytest.approx(expected)
    else:
        assert result == expected
