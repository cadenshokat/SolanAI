import os
from pathlib import Path

import pytest
import responses as http_responses


@pytest.fixture(scope="session", autouse=True)
def _test_env():
    """
    Session-wide env defaults so services don’t crash while importing.
    Each test can override via monkeypatch.
    """
    os.environ.setdefault("DB_PATH", "/tmp/solwatch_test.db")
    os.environ.setdefault("API_PREFIX", "/api/v1")
    os.environ.setdefault("BIRDEYE_API_KEY", "test-key")
    os.environ.setdefault("CMC_API_KEY", "test-key")
    os.environ.setdefault("TW_COOKIES_DIR", "tweet_scraper/cookies")
    yield
    try:
        Path(os.environ["DB_PATH"]).unlink(missing_ok=True)
    except Exception:
        pass


@pytest.fixture
def app():
    from app import create_app

    flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_http():
    """
    requests stubs. Use like:
        mock_http.add(mock_http.GET, "https://...", json={...}, status=200)
    """
    with http_responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def tmp_db(monkeypatch, tmp_path):
    """
    Point services at a temp DB file. Import modules that create tables AFTER using this.
    """
    dbfile = tmp_path / "test.db"
    monkeypatch.setenv("DB_PATH", str(dbfile))
    return dbfile
