import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import json
from helpers.utils import get_students_filter, get_campus, get_project_users_filter
from DF_Client import DF_Client
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from environs import env

env.read_env()

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "data"

if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    client = DF_Client()

    total_data = []

    campus = None
    with open(f'{DATA_DIR}/rio_data.json', 'r') as f:
        campus = json.load(f)
    
    if campus is None:
        logger.error("Unable to read campus data from file...")
        logger.info("Retrieving campus data again.")

        campus = get_campus(
            client.token,
            "Rio de Janeiro"
        )
    
    logger.info(f"Campus ID: {campus['id']}")

    users = None
    with open(f'{DATA_DIR}/piscine_2025_users.json', 'r') as f:
        users = json.load(f)
    
    if users is None:
        logger.error("Unable to read users data from file...")
        logger.info("Retrieving users data again.")

        filters = {
            'pool_year': 2025,
            'primary_campus_id': campus['id']
        }

        users = get_students_filter(
            client.token,
            **filters
        )
    
    for user in users:
        filters = {
            'cursus': 9
        }

        data = get_project_users_filter(
            client.token,
            user,
            **filters
        )

        total_data.append(data)
    
    flat_data = [item for sublist in total_data for item in sublist if item is not None]
    if flat_data is None:
        logger.error("No Pisciners' Project data...")
        raise ValueError("No data to be written...")
    
    logger.info("Trying to save Pisciners' Project data...")
    with open(f'{DATA_DIR}/piscine_2025_projects.json', 'w', encoding='utf-8') as f:
        json.dump(flat_data, f, ensure_ascii=False, indent=4)

    piscine_project_file = Path(f'{DATA_DIR}/piscine_2025_projects.json')
    
    if piscine_project_file.is_file():
        logger.info("Pisciners' Project Data saved successfully!")
        exit(0)
    else:
        logger.error('Unable to save Pisciners Data.')
        exit(1)