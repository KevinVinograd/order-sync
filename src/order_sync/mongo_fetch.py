from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


ORDERS_DB = "MGP-ORDER"
ORDERS_COLLECTION = "Order"
ORDER_LOG_COLLECTION = "OrderLog"
ACCOUNTS_DB = "MGP-ACCOUNT"
ACCOUNTS_COLLECTION = "Accounts"


def get_mongo_client(uri: str) -> MongoClient:
	return MongoClient(uri, retryWrites=True)


def fetch_orders_by_account(uri: str, account_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
	client = get_mongo_client(uri)
	db = client[ORDERS_DB]
	col = db[ORDERS_COLLECTION]
	query = {"accountId": ObjectId(account_id)}
	projection = {
		"number": 1,
		"bookingNumber": 1,
		"dateETD": 1,
		"isMANE": 1,
		"dateETA": 1,
		"isMANI": 1,
		"origin": 1,
		"stopovers": 1,
		"destination": 1,
		"internalClientNumber": 1,
		"isISF": 1,
		"dateISF": 1,
		"createdAt": 1,
		"dateLastUpdate": 1,
	}
	cursor = col.find(query, projection).sort("createdAt", 1)
	if limit:
		cursor = cursor.limit(int(limit))
	return list(cursor)


def fetch_orders_by_ids(uri: str, order_ids: List[str]) -> List[Dict[str, Any]]:
	client = get_mongo_client(uri)
	db = client[ORDERS_DB]
	col = db[ORDERS_COLLECTION]
	ids = [ObjectId(x) for x in order_ids]
	projection = {
		"number": 1,
		"bookingNumber": 1,
		"dateETD": 1,
		"isMANE": 1,
		"dateETA": 1,
		"isMANI": 1,
		"origin": 1,
		"stopovers": 1,
		"destination": 1,
		"internalClientNumber": 1,
		"isISF": 1,
		"dateISF": 1,
		"createdAt": 1,
		"dateLastUpdate": 1,
	}
	return list(col.find({"_id": {"$in": ids}}, projection))


def fetch_account_name(uri: str, account_id: str) -> Optional[str]:
	client = get_mongo_client(uri)
	db = client[ACCOUNTS_DB]
	col = db[ACCOUNTS_COLLECTION]
	doc = col.find_one({"_id": ObjectId(account_id)}, {"accountName": 1})
	if doc and doc.get("accountName"):
		return str(doc.get("accountName"))
	return None


def fetch_updated_order_ids_since(uri: str, account_id: str, since: datetime, batch_size: int = 500) -> List[str]:
	"""Return orderIds updated in OrderLog since 'since' (window by _id)."""
	client = get_mongo_client(uri)
	db = client[ORDERS_DB]
	col = db[ORDER_LOG_COLLECTION]
	# use ObjectId time to window
	min_oid = ObjectId.from_datetime(since)
	q = {"accountId": ObjectId(account_id), "_id": {"$gt": min_oid}}
	proj = {"orderId": 1}
	order_ids: Set[str] = set()
	cursor = col.find(q, proj).batch_size(batch_size)
	for doc in cursor:
		oid = doc.get("orderId")
		if oid:
			order_ids.add(str(oid))
	return list(order_ids)


def fetch_updated_logs_since(uri: str, account_id: str, since: datetime, batch_size: int = 500) -> List[Dict[str, Any]]:
	"""Return detailed OrderLog entries (orderId, action, date, _id) since timestamp for auditing/verbose."""
	client = get_mongo_client(uri)
	db = client[ORDERS_DB]
	col = db[ORDER_LOG_COLLECTION]
	min_oid = ObjectId.from_datetime(since)
	q = {"accountId": ObjectId(account_id), "_id": {"$gt": min_oid}}
	proj = {"orderId": 1, "action": 1, "date": 1, "_id": 1}
	cursor = col.find(q, proj).sort("_id", 1).batch_size(batch_size)
	return list(cursor)


def fetch_recent_field_changes(uri: str, account_id: str, since: datetime, order_ids: List[str], limit_per_order: int = 3) -> List[Tuple[str, List[Dict[str, Any]]]]:
	"""Return small list of recent fieldChanges per orderId since timestamp for audit logs."""
	client = get_mongo_client(uri)
	db = client[ORDERS_DB]
	col = db[ORDER_LOG_COLLECTION]
	min_oid = ObjectId.from_datetime(since)
	ids = [ObjectId(x) for x in order_ids]
	q = {"accountId": ObjectId(account_id), "orderId": {"$in": ids}, "_id": {"$gt": min_oid}}
	proj = {"orderId": 1, "action": 1, "date": 1, "fieldChanges": 1, "_id": 1}
	cursor = col.find(q, proj).sort("_id", 1)
	by_order: Dict[str, List[Dict[str, Any]]] = {}
	for doc in cursor:
		key = str(doc.get("orderId")) if doc.get("orderId") is not None else None
		if not key:
			continue
		entry = {
			"action": doc.get("action"),
			"date": doc.get("date"),
			"changes": []
		}
		changes = doc.get("fieldChanges") or []
		for ch in changes[:5]:
			entry["changes"].append({
				"field": ch.get("fieldName") or ch.get("fieldLabel"),
				"old": ch.get("oldValue"),
				"new": ch.get("newValue"),
			})
		by_order.setdefault(key, []).append(entry)
	# Truncate per order
	out: List[Tuple[str, List[Dict[str, Any]]]] = []
	for oid, entries in by_order.items():
		out.append((oid, entries[-limit_per_order:]))
	return out
