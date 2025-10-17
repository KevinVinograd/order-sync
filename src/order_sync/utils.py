import json
from datetime import datetime, date
from dateutil import parser as dtparser
from typing import Any, Dict, Iterable, List, Optional


ISO_FORMAT = "%Y-%m-%d"


def parse_iso_datetime(value: str) -> datetime:
	return dtparser.parse(value)


def is_same_day(dt: datetime, day: date) -> bool:
	return dt.date() == day


def filter_orders_today(orders: List[Dict[str, Any]], today: Optional[date] = None) -> List[Dict[str, Any]]:
	if today is None:
		today = date.today()
	filtered: List[Dict[str, Any]] = []
	for o in orders:
		ref = o.get("updatedAt") or o.get("date") or o.get("createdAt")
		if not ref:
			continue
		try:
			dt = parse_iso_datetime(str(ref))
		except Exception:
			continue
		if is_same_day(dt, today):
			filtered.append(o)
	return filtered


def load_json_stream(stream: Any) -> Any:
	data = json.load(stream)
	return data


def to_json(obj: Any) -> str:
	return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def coerce_datetime_like(value: Any) -> Optional[datetime]:
	"""Accepts a datetime, string, or {"$date": str} and returns datetime or None."""
	if value is None:
		return None
	if isinstance(value, datetime):
		return value
	if isinstance(value, dict) and "$date" in value:
		try:
			return parse_iso_datetime(str(value["$date"]))
		except Exception:
			return None
	if isinstance(value, str):
		try:
			return parse_iso_datetime(value)
		except Exception:
			return None
	return None


def format_date_ymd(value: Any) -> Optional[str]:
	dt = coerce_datetime_like(value)
	return dt.date().isoformat() if dt else None


def yes_no(value: Any) -> str:
	return "YES" if bool(value) else "NO"
