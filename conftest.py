import pytest
import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("BASE_URL")

@pytest.fixture(scope="session")
def api_request_context():
    with sync_playwright() as p:
        request_context = p.request.new_context(base_url=BASE_URL)
        yield request_context
        request_context.dispose()