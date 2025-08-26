# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from pathlib import Path
from random import choice as randomchoice
from modules.logging_config import debug, info, error

##############################

# RANDOM FAKE USER AGENT

##############################

def pick_a_random_user_agent(user_agent_file):
    if not user_agent_file.exists():
        error(f"User agent file not found: {user_agent_file}")
        return "Mozilla/5.0"  # fallback user agent

    try:
        with user_agent_file.open("r", encoding="utf-8") as f:
            agents = [line.strip() for line in f if line.strip()]
    except Exception as e:
        error(f"Failed to read user agent file: {e}")
        return "Mozilla/5.0"

    if not agents:
        error(f"No valid user agents found in {user_agent_file}")
        return "Mozilla/5.0"

    chosen_agent = randomchoice(agents)
    debug(f"Selected User-Agent: {chosen_agent}")
    return chosen_agent
