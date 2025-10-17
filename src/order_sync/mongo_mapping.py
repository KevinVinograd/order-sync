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
	"ISF",
	"Fecha de ISF",
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
	confirmed_etd = yes_no(doc.get("isBookingConfirmed"))
	eta = format_date_ymd(doc.get("dateETA"))
	confirmed_eta = yes_no(doc.get("isConfirmBLReceived"))
	booking = doc.get("bookingNumber")
	mbl = doc.get("bookingNumber")  # si hay un campo MBL distinto, cambiar aquí
	pol = doc.get("origin")
	ts = extract_first_stopover_name(doc)
	pod = doc.get("destination")
	final_destination = doc.get("destination")
	isf = yes_no(doc.get("isISF"))
	fecha_isf = format_date_ymd(doc.get("dateISF"))

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
		"ISF": isf,
		"Fecha de ISF": fecha_isf,
		"orderId": order_id,
		"__createdAt": created_at,
		"__lastUpdateAt": last_update_at,
	}
