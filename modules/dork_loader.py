# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
import json
from pathlib import Path
from modules.logging_config import debug, info, error

##############################

# LOAD DORKS WITH SECTIONS

##############################

def load_dorks(dork_file_path, target):
    dork_file = Path(dork_file_path)

    if not dork_file.exists():
        error(f"Dork file does not exist: {dork_file}")
        raise FileNotFoundError(f"Dork file not found: {dork_file}")

    if not dork_file.is_file():
        error(f"Path is not a regular file: {dork_file}")
        raise ValueError(f"Invalid dork file: {dork_file}")

    try:
        with dork_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        error(f"Error reading or parsing dork file '{dork_file}': {e}")
        raise

    # Replace {target} in all queries per section
    dork_sections = {}
    total_queries = 0
    for section, queries in data.items():
        processed_queries = []
        for query in queries:
            try:
                replaced_query = query.replace("{target}", target)
                processed_queries.append(replaced_query)
            except Exception as e:
                error(f"Error processing query in section '{section}': '{query}': {e}")
                continue
        dork_sections[section] = processed_queries
        total_queries += len(processed_queries)

    info(f"Loaded {total_queries} valid dorks across {len(dork_sections)} sections from {dork_file}")
    debug(f"Dork Sections and Queries: {dork_sections}")

    return dork_sections
