from typing import List, Dict, Any
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, date, UTC
import uuid
import random

def remove_duplicates_set(lst: List[int]) -> List[int]:
    return list(set(lst))

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def model_list_to_dict(model_list: List[DeclarativeBase]) -> Dict[str, List[Dict[str, Any]]]:
    if not model_list:
        return {}

    model_name = model_list[0].__class__.__name__
    return {
        model_name: [
            {column.name: serialize_datetime(getattr(item, column.name))
             for column in item.__table__.columns.values()}
            for item in model_list
        ]
    }

def generate_unique_s3_key():
    now = datetime.now(UTC)
    unique_id = uuid.uuid4()
    return f"{now.strftime('%Y%m%d_%H%M%S')}_{str(unique_id)}"