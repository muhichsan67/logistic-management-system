from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.admin import CourierUpdate, SystemSettingsUpdate
from app.services.admin_service import escape_like
from app.services.dashboard_service import build_buckets, fill_zero, period_start


def test_period_ranges():
    today = date(2026, 10, 17)
    assert period_start("7d", today) == (date(2026, 10, 11), "day")
    assert period_start("30d", today) == (date(2026, 9, 18), "day")
    assert period_start("12m", today) == (date(2025, 11, 1), "month")
    assert period_start("12m", date(2026, 1, 5)) == (date(2025, 2, 1), "month")


def test_buckets_are_complete_and_zero_filled():
    days = build_buckets(date(2026, 10, 11), date(2026, 10, 17), "day")
    assert len(days) == 7
    points = fill_zero(days, {date(2026, 10, 13): 4})
    assert [p.count for p in points] == [0, 0, 4, 0, 0, 0, 0]
    months = build_buckets(date(2025, 11, 1), date(2026, 10, 17), "month")
    assert len(months) == 12 and months[0] == date(2025, 11, 1) and months[-1] == date(2026, 10, 1)


def test_year_rollover_month_buckets():
    m = build_buckets(date(2025, 11, 1), date(2026, 2, 10), "month")
    assert m == [date(2025, 11, 1), date(2025, 12, 1), date(2026, 1, 1), date(2026, 2, 1)]


def test_escape_like():
    assert escape_like("50%_off\\") == "50\\%\\_off\\\\"


@pytest.mark.parametrize("bad", ["0", "-5", "abc", "1.5", "1234567", ""])
def test_settings_reject_non_positive_int(bad):
    with pytest.raises(ValidationError):
        SystemSettingsUpdate(auto_complete_days=bad)


def test_settings_accept_str_or_int_and_require_one():
    assert SystemSettingsUpdate(auto_complete_days=3).to_dict() == {"auto_complete_days": "3"}
    assert SystemSettingsUpdate(pending_alert_timeout_minutes="45").to_dict() == {
        "pending_alert_timeout_minutes": "45"}
    with pytest.raises(ValidationError):
        SystemSettingsUpdate()


def test_courier_update_requires_a_field():
    with pytest.raises(ValidationError):
        CourierUpdate()
    assert CourierUpdate(name="Budi Kurir").name == "Budi Kurir"
