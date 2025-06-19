"""
This file contains the process of initital extraction, in which we're going to get and create the .json files to the basic set of data that we need:

- Cursus.
- Campuses.

Since these are the data that's not going to change and we need it to specify the :campus_id for example.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import json
from helpers.utils import get_all_cursus, get_campus, get_acess_token
from environs import env

env.read_env()

CLIENT_ID = env.str("CLIENT_ID")
CLIENT_SECRET = env.str("CLIENT_SECRET")
TOKEN_URL = env.str("TOKEN_URL")

BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE_DIR / "const_data"

if __name__ == '__main__':
    access_token = get_acess_token(
        CLIENT_ID,
        CLIENT_SECRET,
        TOKEN_URL
    )

    cursus_data = get_all_cursus(
        access_token,
    )

    rio_data = get_campus(
        access_token
    )

    with open(f'{DATA_DIR}/cursus_data.json', 'w', encoding='utf-8') as f:
        json.dump(cursus_data, f, ensure_ascii=False, indent=4)
    
    with open(f'{DATA_DIR}/rio_data.json', 'w', encoding='utf-8') as f:
        json.dump(rio_data, f, ensure_ascii=False, indent=4)