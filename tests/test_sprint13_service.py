from datetime import date, timedelta

from app.services.report_service import UPCOMING_RENEWAL_DAYS


def test_upcoming_window_constant():
    assert UPCOMING_RENEWAL_DAYS == 30
    assert date.today() + timedelta(days=30) > date.today()
