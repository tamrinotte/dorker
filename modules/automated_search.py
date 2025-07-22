# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from time import sleep
from pathlib import Path
from urllib.parse import quote_plus
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from modules.logging_config import debug, info, error
from random import uniform as randomuniform
from sys import exit as sysexit

##############################

# BUILD SEARCH URL

##############################

def build_search_url(engine, query):
    encoded = quote_plus(query)
    if engine == "duckduckgo":
        return f"https://duckduckgo.com/?q={encoded}"
    elif engine == "google":
        return f"https://www.google.com/search?q={encoded}"
    return None

##############################

# SEARCH AUTOMATICALLY

##############################

def search_automatically(target, engine, user_agent, dork_sections, is_headless_mode_on, geckodriver):
    total_sections = len(dork_sections)
    print(f"Starting automated search for target '{target}' using {engine}. Total sections: {total_sections}")

    results_dir = Path("results", target)
    results_dir.mkdir(parents=True, exist_ok=True)

    drivers = []  # Keep all driver instances to prevent garbage collection and keep windows open

    for window_index, (section_name, query_list) in enumerate(dork_sections.items()):
        firefox_options = Options()
        if is_headless_mode_on:
            firefox_options.add_argument("--headless")
        firefox_options.set_preference("dom.webdriver.enabled", False)  # hides navigator.webdriver
        firefox_options.set_preference("media.peerconnection.enabled", False)  # disables WebRTC leaks
        firefox_options.set_preference("privacy.resistFingerprinting", True)  # reduces fingerprinting surface
        firefox_options.set_preference("privacy.trackingprotection.enabled", True)  # blocks trackers
        firefox_options.set_preference("general.useragent.override", user_agent)  # spoof user agent

        # Add these Firefox prefs for stealth:
        firefox_options.set_preference("security.fileuri.strict_origin_policy", False)  # reduces CORS errors that might reveal automation
        firefox_options.set_preference("webdriver.load.strategy", "unstable")  # can make page load appear less 'scripted'
        firefox_options.set_preference("devtools.console.stdout.content", True)  # avoid alerting devtools detection
        firefox_options.set_preference("dom.webnotifications.enabled", False)  # disable notifications

        # Disable WebGL to reduce fingerprinting surface:
        firefox_options.set_preference("webgl.disabled", True)

        # Block telemetry & data reporting to Mozilla:
        firefox_options.set_preference("toolkit.telemetry.reportingpolicy.firstRun", False)
        firefox_options.set_preference("datareporting.healthreport.uploadEnabled", False)
        firefox_options.set_preference("datareporting.policy.dataSubmissionEnabled", False)

        # Override permissions to avoid permission popups:
        firefox_options.set_preference("permissions.default.desktop-notification", 2)

        try:
            if geckodriver:
                gecko_path = str(Path(geckodriver).resolve())
                service = FirefoxService(executable_path=gecko_path)
            else:
                service = FirefoxService()
            driver = webdriver.Firefox(service=service, options=firefox_options)
            driver.set_page_load_timeout(30)
        except Exception as e:
            error(f"[{section_name}] Failed to start GeckoDriver (Firefox): {e}")
            continue

        info(f"[{section_name}] Opening window with {len(query_list)} tabs.")
        print(f"[{window_index+1}/{total_sections}] Section '{section_name}' started. {len(query_list)} queries to process.")
        drivers.append(driver)  # Store driver so it stays alive

        for index, query in enumerate(query_list):
            search_url = build_search_url(engine, query.replace("{target}", target))
            if not search_url:
                error(f"Unsupported engine: {engine}")
                continue

            try:
                if index == 0:
                    driver.get(search_url)
                else:
                    driver.execute_script(f"window.open('{search_url}', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                sleep(randomuniform(1.5, 4.2))

                screenshot_path = results_dir / f"window_{window_index:02}_tab_{index+1:02}.png"
                driver.save_screenshot(str(screenshot_path))
                debug(f"[{section_name}] Saved screenshot to {screenshot_path}")

            except Exception as e:
                error(f"[{section_name}] Failed to load query '{query}': {e}")
        
        print(f"[{window_index+1}/{total_sections}] Section '{section_name}' completed.")

    info("Automated search has been completed.")

    print(f"\nScreenshots are located at: {results_dir}")
    print("\nAll section windows opened.")
    print("Please inspect them manually.")

    while True:
        response = input("When you are done type \"exit\" and press enter to close all browser windows and to exit the program: ").lower().strip()
        if response == "exit":
            info("Closing all browser windows...")
            for driver in drivers:
                try:
                    driver.quit()
                except Exception as e:
                    error(f"Error: {e}")
            sysexit()