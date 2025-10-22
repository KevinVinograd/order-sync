from typing import Any, Dict, Optional

from .utils import format_date_ymd, yes_no


REPORT_COLUMNS_VISIBLE = [
	"REF",
	"ETD (fecha)",
	"Confirmed ETD",
	"ETA (fecha)",
	"Confirmed ETA",
	"Booking",
	"MBL",
	"POL",
	"T/S",
	"POD",
	"Final destination",
	"Internal client number",
	"ISF",
	"Fecha de ISF",
	"Customs clearance",
	"Fecha de customs clearance",
	"Empty return",
	"Fecha de empty return",
]

TECH_COLUMNS = [
	"orderId",
	"__createdAt",
	"__lastUpdateAt",
]

REPORT_COLUMNS = REPORT_COLUMNS_VISIBLE + TECH_COLUMNS


def extract_first_stopover_name(doc: Dict[str, Any]) -> Optional[str]:
	stops = doc.get("stopovers") or []
	if not isinstance(stops, list) or not stops:
		return None
	first = stops[0] or {}
	name = first.get("stopoverName") or first.get("name")
	return name


def map_doc_to_report_row(doc: Dict[str, Any]) -> Dict[str, Any]:
	ref = doc.get("number")
	etd = format_date_ymd(doc.get("dateETD"))
	confirmed_etd = yes_no(doc.get("isMANE"))  # ETD confirmado
	eta = format_date_ymd(doc.get("dateETA"))
	confirmed_eta = yes_no(doc.get("isMANI"))  # ETA confirmado
	booking = doc.get("bookingNumber")
	mbl = doc.get("bookingNumber")
	pol = doc.get("origin")
	ts = extract_first_stopover_name(doc)
	pod = doc.get("destination")
	final_destination = doc.get("destination")
	internal_client_number = doc.get("internalClientNumber")
	isf = yes_no(doc.get("isISF"))
	fecha_isf = format_date_ymd(doc.get("dateISF"))
	# Defaults for now
	customs_clearance = "NO"
	fecha_customs_clearance = None
	empty_return = "NO"
	fecha_empty_return = None

	order_id = str(doc.get("_id")) if doc.get("_id") is not None else None
	created_at = format_date_ymd(doc.get("createdAt"))
	last_update_at = format_date_ymd(doc.get("dateLastUpdate"))

	return {
		"REF": ref,
		"ETD (fecha)": etd,
		"Confirmed ETD": confirmed_etd,
		"ETA (fecha)": eta,
		"Confirmed ETA": confirmed_eta,
		"Booking": booking,
		"MBL": mbl,
		"POL": pol,
		"T/S": ts,
		"POD": pod,
		"Final destination": final_destination,
		"Internal client number": internal_client_number,
		"ISF": isf,
		"Fecha de ISF": fecha_isf,
		"Customs clearance": customs_clearance,
		"Fecha de customs clearance": fecha_customs_clearance,
		"Empty return": empty_return,
		"Fecha de empty return": fecha_empty_return,
		"orderId": order_id,
		"__createdAt": created_at,
		"__lastUpdateAt": last_update_at,
	}
