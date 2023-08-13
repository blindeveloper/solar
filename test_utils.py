from app.utils import extract_hours_from_ts


def test_extract_hours_from_ts():
    assert extract_hours_from_ts(
        '2023-08-11T02:55:00', 1) == '2023-08-11 01:55:00'
    assert extract_hours_from_ts(
        '2023-08-11T02:55:00', 0.5) == '2023-08-11 02:25:00'
    assert extract_hours_from_ts(
        '2023-08-11T02:55:00', 2) == '2023-08-11 00:55:00'
