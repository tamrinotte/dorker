# -*- coding: utf-8 -*-

# MODULES AND/OR LIBRARIES
from time import sleep, time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    JavascriptException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from modules.logging_config import debug, info, error
from modules.screenshot import save_full_page_screenshot
from random import uniform as randomuniform
from sys import exit as sysexit

##############################

# CONFIGURATION / DEFAULTS

##############################

DEFAULT_PAGE_LOAD_TIMEOUT = 30
DEFAULT_NETWORK_QUIET_TIMEOUT = 5
DEFAULT_CAPTCHA_POLL = 3

##############################

# HELPERS

##############################

def build_search_url(engine, query):
    encoded = quote_plus(query)
    engine = engine.lower()
    if engine == "duckduckgo":
        return f"https://duckduckgo.com/?q={encoded}"
    if engine == "startpage":
        return f"https://www.startpage.com/search?q={encoded}"
    return None

def make_firefox_options(user_agent, headless):
    opts = Options()
    if headless:
        opts.add_argument("--headless")

    # Stealth-ish preferences
    opts.set_preference("dom.webdriver.enabled", False)
    opts.set_preference("media.peerconnection.enabled", False)
    opts.set_preference("privacy.resistFingerprinting", True)
    opts.set_preference("privacy.trackingprotection.enabled", True)
    opts.set_preference("general.useragent.override", user_agent)

    opts.set_preference("security.fileuri.strict_origin_policy", False)
    opts.set_preference("webdriver.load.strategy", "unstable")
    opts.set_preference("devtools.console.stdout.content", True)
    opts.set_preference("dom.webnotifications.enabled", False)

    opts.set_preference("webgl.disabled", True)

    opts.set_preference("toolkit.telemetry.reportingpolicy.firstRun", False)
    opts.set_preference("datareporting.healthreport.uploadEnabled", False)
    opts.set_preference("datareporting.policy.dataSubmissionEnabled", False)

    opts.set_preference("permissions.default.desktop-notification", 2)
    return opts

##############################

# CAPTCHA DETECTION & WAIT

##############################

def page_body_text(driver):
    try:
        return driver.find_element(By.TAG_NAME, "body").text.lower()
    except Exception:
        return ""

def is_startpage_captcha(driver):
    try:
        url = driver.current_url.lower()
    except WebDriverException:
        return False

    if "startpage.com/sp/captcha" in url:
        return True

    body = page_body_text(driver)
    indicators = [
        "please verify", "verify you're", "are you human", "please complete",
        "security check", "to continue, please", "enter the characters you see",
        "please show you're human", "unusual traffic"
    ]
    if any(tok in body for tok in indicators):
        return True

    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for fr in iframes:
            src = (fr.get_attribute("src") or "").lower()
            if any(provider in src for provider in ("recaptcha", "hcaptcha", "captcha", "startpage.com/sp/captcha")):
                return True
    except Exception:
        pass

    return False

def wait_for_manual_captcha_solve(
    driver,
    poll_interval = DEFAULT_CAPTCHA_POLL,
    timeout = None,
    context = None
):
    start = time()
    while True:
        if not is_startpage_captcha(driver):
            info("Captcha cleared.")
            return True
        if timeout and (time() - start) > timeout:
            error("Captcha wait timed out.")
            return False
        if context:
            wnd, tab, section = context
            info(f"Captcha detected in window {wnd} tab {tab} (section={section}) — please solve it in the browser.")
        else:
            info("Captcha detected — please solve it in the browser.")
        sleep(poll_interval)

##############################

# PAGE LOAD WAIT

##############################

def wait_for_page_load(
    driver,
    timeout = DEFAULT_PAGE_LOAD_TIMEOUT,
    check_selector = None,
    wait_for_network_quiet = True
):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        debug("document.readyState did not become 'complete' within timeout; continuing.")

    if wait_for_network_quiet:
        try:
            WebDriverWait(driver, DEFAULT_NETWORK_QUIET_TIMEOUT).until(
                lambda d: d.execute_script("return window.jQuery ? jQuery.active === 0 : true")
            )
        except (TimeoutException, JavascriptException):
            debug("Network quiet check timed out or failed; continuing.")

    if check_selector:
        try:
            WebDriverWait(
                driver,
                timeout
            ).until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, check_selector)
                )
            )
        except TimeoutException:
            debug(f"Selector '{check_selector}' not found within timeout; continuing.")

##############################

# MAIN SEARCH FUNCTION

##############################

def search_automatically(
    target,
    engine,
    user_agent,
    dork_sections,
    is_headless_mode_on,
    geckodriver,
    min_delay,
    max_delay,
    page_load_timeout = DEFAULT_PAGE_LOAD_TIMEOUT,
):
    total_sections = len(dork_sections)
    info(f"Starting automated search for target '{target}' using {engine}. Total sections: {total_sections}")

    results_dir = Path("results") / target
    results_dir.mkdir(parents=True, exist_ok=True)

    drivers = []  # keep references so GC doesn't close them

    for window_index, (section_name, query_list) in enumerate(dork_sections.items(), start=1):
        opts = make_firefox_options(user_agent=user_agent, headless=is_headless_mode_on)

        try:
            if geckodriver:
                gecko_path = str(Path(geckodriver).resolve())
                service = FirefoxService(executable_path=gecko_path)
            else:
                service = FirefoxService()
            driver = webdriver.Firefox(service=service, options=opts)
            driver.set_page_load_timeout(page_load_timeout)
        except WebDriverException as e:
            error(f"[{section_name}] Failed to start GeckoDriver (Firefox): {e}")
            continue

        info(f"[{section_name}] Opening window with {len(query_list)} tabs.")
        debug(
            f"[{window_index}/{total_sections}] Section '{section_name}' started. "
            f"{len(query_list)} queries to process."
        )
        drivers.append(driver)

        for tab_index, query in enumerate(query_list, start=1):
            search_url = build_search_url(engine, query.replace("{target}", target))
            if not search_url:
                error(f"Unsupported engine: {engine}")
                continue

            try:
                if tab_index == 1:
                    driver.get(search_url)
                else:
                    driver.execute_script("window.open(arguments[0], '_blank');", search_url)
                    driver.switch_to.window(driver.window_handles[-1])

                selector = "#links" if engine.lower() == "duckduckgo" else None
                wait_for_page_load(driver, timeout=page_load_timeout, check_selector=selector)

                if is_startpage_captcha(driver):
                    # log helpful info for finding the window/tab
                    captcha_url = driver.current_url
                    info(
                        f"Startpage captcha detected at URL: {captcha_url} "
                        f"(window={window_index} tab={tab_index}, section={section_name})"
                    )
                    solved = wait_for_manual_captcha_solve(
                        driver,
                        poll_interval=DEFAULT_CAPTCHA_POLL,
                        timeout=None,
                        context=(window_index,
                            tab_index,
                            section_name,
                        )
                    )
                    if not solved:
                        error(f"[{section_name}] Captcha not solved within timeout; skipping this query.")
                        continue

                sleep(randomuniform(min_delay, max_delay))

                screenshot_path = results_dir / f"window_{window_index:02}_tab_{tab_index:02}.png"
                saved = save_full_page_screenshot(driver=driver, path=str(screenshot_path))
                if saved:
                    debug(f"[{section_name}] Saved screenshot to {screenshot_path}")
                else:
                    error(f"[{section_name}] Failed to save screenshot for tab {tab_index}")

            except TimeoutException as e:
                error(f"[{section_name}] Timeout loading query '{query}': {e}")
            except WebDriverException as e:
                error(f"[{section_name}] WebDriver error for query '{query}': {e}")
            except Exception as e:
                error(f"[{section_name}] Unexpected error for query '{query}': {e}")

        debug(f"[{window_index}/{total_sections}] Section '{section_name}' completed.")

    info("Automated search has been completed.")
    info(f"Screenshots are located at: {results_dir}")
    info("All section windows opened. Please inspect them manually.")

    try:
        while True:
            response = input(
                "When you are done type \"exit\" and press enter to close all browser windows "
                "and to exit the program: "
            ).strip().lower()
            if response == "exit":
                info("Closing all browser windows...")
                for driver in drivers:
                    try:
                        driver.quit()
                    except Exception as e:
                        error(f"Error closing driver: {e}")
                sysexit()
    except KeyboardInterrupt:
        info("Interrupted by user — closing browsers.")
        for driver in drivers:
            try:
                driver.quit()
            except Exception:
                pass
