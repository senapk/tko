import datetime as dt

from tko.logger.delta import Delta, DeltaMode, DeltaAction


def make_datetime(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, Delta.format)


class TestDeltaHelpers:
    def test_encode_and_decode_format_round_trip(self):
        value = make_datetime("2026-04-28 14:35:42")

        encoded = Delta.encode_format(value)

        assert encoded == "2026-04-28 14:35:42"
        assert Delta.decode_format(encoded) == value

    def test_encode_timedelta_and_string_representation(self):
        delta = Delta()
        delta.datetime = make_datetime("2026-04-28 14:35:42")
        delta.elapsed = dt.timedelta(minutes=5, seconds=7)
        delta.accumulated = dt.timedelta(minutes=12, seconds=3)

        assert Delta.encode_timedelta(dt.timedelta(minutes=3, seconds=9)) == "003:09"
        assert str(delta) == "datetime:2026-04-28 14:35:42, elapsed:005:07, acc:012:03"

    def test_format_h_min_week_day_and_next_day(self):
        assert Delta.format_h_min(-1) == "00:00"
        assert Delta.format_h_min(2.5) == "02h 30m"
        assert Delta.week_day("2026-04-28") == "Tuesday"
        assert Delta.next_day("2026-04-28") == "2026-04-29"


class TestDeltaCreate:
    def test_create_without_inc_time_keeps_accumulated_and_ignores_past_dates(self):
        base = Delta()
        base.accumulated = dt.timedelta(minutes=10)
        base.datetime = make_datetime("2026-04-28 10:00:00")

        created = Delta().create_from(
            DeltaMode(DeltaAction.without_inc_time),
            base,
            make_datetime("2026-04-28 10:03:30"),
        )

        assert created.mode is not None
        assert created.elapsed == dt.timedelta(minutes=3, seconds=30)
        assert created.accumulated == dt.timedelta(minutes=10)

        reversed_time = Delta().create_from(
            DeltaMode(DeltaAction.without_inc_time),
            base,
            make_datetime("2026-04-28 09:59:00"),
        )
        assert reversed_time.elapsed == dt.timedelta(0)
        assert reversed_time.accumulated == dt.timedelta(minutes=10)

    def test_create_incrementing_time_adds_positive_elapsed(self):
        base = Delta()
        base.accumulated = dt.timedelta(minutes=4)
        base.datetime = make_datetime("2026-04-28 10:00:00")

        created = Delta().create_from(
            DeltaMode(DeltaAction.incrementing_time),
            base,
            make_datetime("2026-04-28 10:01:15"),
        )

        assert created.elapsed == dt.timedelta(minutes=1, seconds=15)
        assert created.accumulated == dt.timedelta(minutes=5, seconds=15)

    def test_create_with_time_threshold_only_accumulates_below_limit(self):
        base = Delta()
        base.accumulated = dt.timedelta(minutes=7)
        base.datetime = make_datetime("2026-04-28 10:00:00")
        mode = DeltaMode(DeltaAction.with_time_threshold, minutes_limit=30)

        accepted = Delta().create_from(mode, base, make_datetime("2026-04-28 10:20:00"))
        assert accepted.accumulated == dt.timedelta(minutes=27)

        rejected = Delta().create_from(mode, base, make_datetime("2026-04-28 10:45:00"))
        assert rejected.elapsed == dt.timedelta(minutes=45)
        assert rejected.accumulated == dt.timedelta(minutes=7)

    def test_create_with_no_previous_item_starts_from_zero_elapsed(self):
        moment = make_datetime("2026-04-28 10:00:00")

        created = Delta().create_from(
            DeltaMode(DeltaAction.incrementing_time),
            None,
            moment,
        )

        assert created.datetime == moment
        assert created.elapsed == dt.timedelta(0)
        assert created.accumulated == dt.timedelta(0)