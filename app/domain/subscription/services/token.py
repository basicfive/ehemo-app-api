from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz

def calculate_next_refill_date(timezone: str, current_time: Optional[datetime] = None) -> datetime:
    """
    주어진 timezone의 다음 달 자정 시간을 UTC로 계산

    Args:
        timezone (str): 사용자의 timezone (예: 'Asia/Seoul')
        current_time (datetime): 기준이 되는 시간 (UTC)

    Returns:
        datetime: 다음 리필 시간 (UTC)
    """
    if not current_time.tzinfo:
        raise ValueError("current_time must be timezone-aware datetime")
    if current_time.tzinfo != pytz.UTC:
        raise ValueError("current_time must be in UTC")

    tz = pytz.timezone(timezone)
    local_time = current_time.astimezone(tz)

    next_month = local_time + relativedelta(month=1)

    next_refill = next_month.replace(
        day=next_month.day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    return next_refill.astimezone(pytz.UTC)

