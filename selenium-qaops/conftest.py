"""
Configuración Pytest QAOps (Ayesa Digital) para pruebas Selenium E2E y sincronización
en tiempo real con el Hub ALM (Jira Xray / TestLink / Redmine).
"""

from __future__ import annotations

import os
import time
from typing import Dict, Generator, List

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.webdriver import WebDriver

BASE_URL = os.environ.get("ADESLAS_BASE_URL", "http://127.0.0.1:8080")
EXECUTION_RESULTS: List[Dict[str, object]] = []


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "xray(key): Vincula el test automatizado con el Test Case de Jira Xray / TestLink / Redmine"
    )


def create_headless_driver() -> WebDriver:
    """Crea una instancia de WebDriver Headless probando Chrome y luego Microsoft Edge."""
    browser_pref = os.environ.get("QAOPS_BROWSER", "auto").lower()

    if browser_pref in ("auto", "chrome"):
        try:
            opts = ChromeOptions()
            opts.add_argument("--headless=new")
            opts.add_argument("--window-size=1440,950")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--no-sandbox")
            return webdriver.Chrome(options=opts)
        except Exception:
            if browser_pref == "chrome":
                raise

    opts_edge = EdgeOptions()
    opts_edge.add_argument("--headless=new")
    opts_edge.add_argument("--window-size=1440,950")
    opts_edge.add_argument("--disable-gpu")
    return webdriver.Edge(options=opts_edge)


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="module")
def driver() -> Generator[WebDriver, None, None]:
    drv = create_headless_driver()
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call":
        marker = item.get_closest_marker("xray")
        if marker and marker.args:
            tc_key = marker.args[0]
            EXECUTION_RESULTS.append(
                {
                    "key": tc_key,
                    "status": "PASSED" if report.passed else "FAILED",
                    "durationMs": int(report.duration * 1000),
                }
            )


def pytest_sessionfinish(session, exitstatus):
    if EXECUTION_RESULTS:
        try:
            requests.post(
                f"{BASE_URL}/api/v1/qaops/test-runs",
                json={"results": EXECUTION_RESULTS},
                timeout=3,
            )
        except Exception:
            pass
