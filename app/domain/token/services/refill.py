from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
import calendar

def calculate_next_refill_date(
        timezone: str,
        current_time: datetime,
        initial_purchase_time: datetime,
) -> datetime:
    """
    initial_purchase_time의 일자를 기준으로 다음 달의 리필 시간을 UTC로 계산
    만약 다음 달에 해당 일자가 없다면 해당 월의 마지막 날을 반환

    Args:
        timezone (str): 사용자의 timezone (예: 'Asia/Seoul')
        current_time (datetime): 기준이 되는 시간 (UTC)
        initial_purchase_time (datetime): 구독권 첫 구매 날짜 (UTC)

    Returns:
        datetime: 다음 리필 시간 (UTC)
    """
    if not current_time.tzinfo:
        raise ValueError("current_time must be timezone-aware datetime")
    if not initial_purchase_time.tzinfo:
        raise ValueError("initial_purchase_time must be timezone-aware datetime")
    if current_time.tzinfo != pytz.UTC or initial_purchase_time.tzinfo != pytz.UTC:
        raise ValueError("Both times must be in UTC")

    tz = pytz.timezone(timezone)
    local_current = current_time.astimezone(tz)
    local_initial = initial_purchase_time.astimezone(tz)

    # 다음 달 계산
    next_month = local_current + relativedelta(months=1)

    # 다음 달의 마지막 날 계산
    _, last_day = calendar.monthrange(next_month.year, next_month.month)

    # initial_purchase_time의 일자와 다음 달의 마지막 날을 비교
    target_day = min(local_initial.day, last_day)

    next_refill = next_month.replace(
        day=target_day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    return next_refill.astimezone(pytz.UTC)