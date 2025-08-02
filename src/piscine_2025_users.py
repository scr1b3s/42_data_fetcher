import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import json
from helpers.utils import get_students_filter, get_campus
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

    filters = {
            'pool_year': 2025,
            'primary_campus_id': campus['id']
    }

    pisciners_data = get_students_filter(
        client.token,
        **filters
    )

    if pisciners_data is None:
        logger.error("No Pisciners data...")
        raise ValueError("No data to be written...")

    logger.info('Trying to save Pisciners data...')
    with open(f'{DATA_DIR}/piscine_2025_users.json', 'w', encoding='utf-8') as f:
        json.dump(pisciners_data, f, ensure_ascii=False, indent=4)
    
    pisciners_data_file = Path(f'{DATA_DIR}/piscine_2025_users.json')
    
    if pisciners_data_file.is_file():
        logger.info('Pisciners Data saved successfully!')
        exit(0)
    else:
        logger.error('Unable to save Pisciners Data.')
        exit(1)