import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))

import logging
from FT_Extractor import FT_Extractor
from environs import env

env.read_env()

FILTERS = {"campus": {"filter[city]": "Rio de Janeiro"}}


def initial_extraction():
    logger = logging.getLogger("INITIAL_EXTRACTION")
    extractor = FT_Extractor()

    logger.info(
        "Initiating Initial Extraction: Campus, Cursus and Projects for Cursus..."
    )

    campus_data = extractor.basic_extraction("campus", **FILTERS["campus"])
    cursus_data = extractor.basic_extraction(
        "cursus",
    )

    projects_data = extractor.filtered_extraction(
        "projects", "cursus/{cursus_id}/projects", {"cursus_id": 9}
    )

    extractor.set_json("campus_data", campus_data)
    extractor.set_json("cursus_data", cursus_data)
    extractor.set_json("c_piscine_projects", projects_data)


if __name__ == "__main__":
    initial_extraction()
