from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Order:
	userId: str
	orderId: str
	date: str  # ISO8601 string
	status: Optional[str] = None
	total: Optional[float] = None
	updatedAt: Optional[str] = None  # ISO8601 string
	data: Dict[str, Any] = field(default_factory=dict)

	@staticmethod
	def from_dict(d: Dict[str, Any]) -> "Order":
		user_id = str(d.get("userId") or d.get("user_id"))
		order_id = str(d.get("orderId") or d.get("order_id"))
		if not user_id or not order_id:
			raise ValueError("userId and orderId are required")
		date = str(d.get("date") or d.get("createdAt") or "")
		status = d.get("status")
		total_val = d.get("total")
		total = float(total_val) if total_val is not None else None
		updated_at = d.get("updatedAt") or d.get("updated_at")
		# Keep extra fields in data
		extra = {k: v for k, v in d.items() if k not in {"userId", "user_id", "orderId", "order_id", "date", "status", "total", "updatedAt", "updated_at"}}
		return Order(
			userId=user_id,
			orderId=order_id,
			date=date,
			status=status,
			total=total,
			updatedAt=updated_at,
			data=extra,
		)


def ensure_list(obj: Any) -> List[Dict[str, Any]]:
	if obj is None:
		return []
	if isinstance(obj, list):
		return obj
	return [obj]
