import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

import json
from DF_Client import DF_Client
import requests

from environs import env

env.read_env()

REQ_URL = env.str("REQ_URL")

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.info("Initiating...")
    client = DF_Client()

    user_id = 234800
    cursus_users_data = requests.get(
        f"{REQ_URL}users/{user_id}/cursus_users",
        headers={"Authorization": f"Bearer {client.token}"}
    )

    logger.info("Writing data...")
    with open(f'{DATA_DIR}/cursus_users_data.json', 'w', encoding='utf-8') as f:
        json.dump(cursus_users_data.json(), f, ensure_ascii=False, indent=4)

    projects_data = requests.get(
        f"{REQ_URL}users/{user_id}/projects_users",
        headers={"Authorization": f"Bearer {client.token}"}
    )

    logger.info("Writing data...")
    with open(f'{DATA_DIR}/project_users.json', 'w', encoding='utf-8') as f:
        json.dump(projects_data.json(), f, ensure_ascii=False, indent=4)