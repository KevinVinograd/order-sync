import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv


@dataclass
class Config:
	mongo_uri: Optional[str]
	output_dir: str
	timezone: Optional[str]
	# Google Drive credentials via env (like other service)
	drive_client_email: Optional[str]
	drive_private_key: Optional[str]
	drive_folder_id: Optional[str]
	# Accounts list to track
	account_ids: List[str]


DEFAULT_OUTPUT_DIR = "./order_sync_output"


def load_env_file(env_file: Optional[str]) -> None:
	if env_file:
		load_dotenv(dotenv_path=env_file, override=False)
	else:
		# auto-load .env if exists in CWD
		cwd_env = Path.cwd() / ".env"
		if cwd_env.exists():
			load_dotenv(dotenv_path=str(cwd_env), override=False)


def get_config() -> Config:
	account_ids_raw = os.getenv("ACCOUNT_IDS", "").strip()
	account_ids = [s.strip() for s in account_ids_raw.split(",") if s.strip()]
	return Config(
		mongo_uri=os.getenv("MONGO_URI"),
		output_dir=os.getenv("OUTPUT_DIR", DEFAULT_OUTPUT_DIR),
		timezone=os.getenv("TZ") or os.getenv("TIMEZONE"),
		drive_client_email=os.getenv("GOOGLE_CLIENT_EMAIL"),
		drive_private_key=os.getenv("GOOGLE_PRIVATE_KEY"),
		drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID"),
		account_ids=account_ids,
	)
