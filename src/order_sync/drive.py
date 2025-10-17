from pathlib import Path
from typing import Tuple, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io


DRIVE_SCOPE = ["https://www.googleapis.com/auth/drive.file"]
TOKEN_URI = "https://oauth2.googleapis.com/token"


def build_drive_client(client_email: str, private_key: str):
	# Normalize private key in case it comes with literal \n characters
	pk = private_key.replace("\\n", "\n")
	info = {
		"type": "service_account",
		"client_email": client_email,
		"private_key": pk,
		"token_uri": TOKEN_URI,
	}
	creds = service_account.Credentials.from_service_account_info(info, scopes=DRIVE_SCOPE)
	return build("drive", "v3", credentials=creds, cache_discovery=False)


def find_file_id_by_name(drive, folder_id: str, name: str) -> Optional[str]:
	q = f"name = '{name}' and '{folder_id}' in parents and trashed = false"
	res = drive.files().list(
		q=q,
		spaces="drive",
		fields="files(id,name)",
		includeItemsFromAllDrives=True,
		supportsAllDrives=True,
	).execute()
	files = res.get("files", [])
	return files[0]["id"] if files else None


def download_file(drive, file_id: str, dest_path: Path) -> Path:
	req = drive.files().get_media(fileId=file_id, supportsAllDrives=True)
	fh = io.FileIO(str(dest_path), mode="wb")
	downloader = MediaIoBaseDownload(fh, req)
	done = False
	while not done:
		status, done = downloader.next_chunk()
	return dest_path


def upload_or_update_file(drive, file_path: Path, folder_id: str) -> Tuple[str, str]:
	name = file_path.name
	q = f"name = '{name}' and '{folder_id}' in parents and trashed = false"
	res = drive.files().list(
		q=q,
		spaces="drive",
		fields="files(id,name)",
		includeItemsFromAllDrives=True,
		supportsAllDrives=True,
	).execute()
	files = res.get("files", [])
	media = MediaFileUpload(str(file_path), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=False)
	if files:
		file_id = files[0]["id"]
		drive.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
		return file_id, "updated"
	metadata = {
		"name": name,
		"parents": [folder_id],
		"mimeType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
	}
	created = drive.files().create(
		body=metadata,
		media_body=media,
		fields="id",
		supportsAllDrives=True,
	).execute()
	return created.get("id"), "created"
