# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from argparse import ArgumentParser
from pathlib import Path
from modules.logging_config import error
from modules.dork_loader import load_dorks
from modules.automated_search import search_automatically
from modules.random_fake_user_agent import pick_a_random_user_agent
from modules.resource_utils import load_resource_path
from modules.domain_detection import is_domain

##############################

# DORKER

##############################

class Dorker:
    def __init__(self, target, engine, is_headless_mode_on, geckodriver, min_delay, max_delay):
        self.target = target
        self.engine = engine.lower()
        self.fake_user_agent_file = load_resource_path("data/fake_user_agents.json")
        self.user_agent = pick_a_random_user_agent(user_agent_file=self.fake_user_agent_file)
        if is_domain(self.target):
            dork_path = load_resource_path("data/url_dorks.json")
        else:
            dork_path = load_resource_path("data/name_dorks.json")
        self.dork_file = dork_path
        self.dork_sections = load_dorks(dork_file_path=self.dork_file, target=self.target)
        self.is_headless_mode_on = is_headless_mode_on
        self.geckodriver = geckodriver
        self.min_delay = min_delay
        self.max_delay = max_delay

    def perform_automated_search(self):
        search_automatically(
            target=self.target,
            engine=self.engine,
            user_agent=self.user_agent,
            dork_sections=self.dork_sections,
            is_headless_mode_on=self.is_headless_mode_on,
            geckodriver=self.geckodriver,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
        )

    def start(self):
        self.perform_automated_search()

##############################

# MAIN FUNCTION

##############################

def main():
    parser = ArgumentParser(description="Dorker: DuckDuckGo/Startpage OSINT Automation")
    parser.add_argument("target", help="Person/Event/Company name or domain to scan")
    parser.add_argument(
        "-e", "--engine",
        choices=["duckduckgo", "startpage"],
        default="duckduckgo",
        help="Search engine to use (default: duckduckgo).",
    )
    parser.add_argument(
        "-hl", "--headless",
        action="store_true",
        help="Run the search in headless mode (no visible browser window).",
    )
    parser.add_argument(
        "-gd", "--geckodriver",
        type=str,
        default=None,
        help="Optional path to a GeckoDriver binary. If not provided, Selenium will auto-manage it.",
    )
    parser.add_argument(
        "-min", "--min_delay",
        type=int,
        default=0,
        help="Optional minimum delay (in seconds) between searches to simulate human-like behavior (default: 0).",
    )
    parser.add_argument(
        "-max", "--max_delay",
        type=int,
        default=1,
        help="Optional maximum delay (in seconds) between searches to simulate human-like behavior (default: 1).",
    )
    args = parser.parse_args()

    try:
        dorker = Dorker(
            target=args.target,
            engine=args.engine,
            is_headless_mode_on=args.headless,
            geckodriver=args.geckodriver,
            min_delay=args.min_delay,
            max_delay=args.max_delay,
        )
        dorker.start()
    except FileNotFoundError as e:
        error(f"File not found error: {e}")
    except Exception as e:
        error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()