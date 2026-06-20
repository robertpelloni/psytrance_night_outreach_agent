import pytest
from src.ai_engine import AIEngine, TokenBudgetExceededException
from src.db_manager import DatabaseManager
from src.config_manager import ConfigManager
import os

@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    cfg_path = str(tmp_path / "config.json")

    db = DatabaseManager()
    cfg = ConfigManager(config_path=cfg_path)

    # Setup test config
    cfg.save_config({
        "openai_daily_budget_tokens": 100,
        "openai_run_budget_tokens": 50,
        "media_library": []
    })

    return db_path, cfg_path, db, cfg

def test_ai_engine_budget_exceeded(mock_env, monkeypatch):
    db_path, cfg_path, db, cfg = mock_env

    # Mock AIEngine logic
    monkeypatch.setattr("src.config_manager.ConfigManager.get", cfg.get)

    engine = AIEngine(api_key="fake")

    # Pre-load DB with tokens
    db.log_ai_usage("gpt-4o", 20, 40, 60) # 60 total

    # Since run limit is 50, and we used 60 this run (assuming it's after start time)
    with pytest.raises(TokenBudgetExceededException) as excinfo:
        engine.check_budget()

    assert "Run token budget exceeded" in str(excinfo.value)

    # Test Daily Limit Exceeded
    cfg.save_config({
        "openai_daily_budget_tokens": 100,
        "openai_run_budget_tokens": 200,
        "media_library": []
    })

    db.log_ai_usage("gpt-4o", 20, 30, 50) # +50 = 110 total

    with pytest.raises(TokenBudgetExceededException) as excinfo:
        engine.check_budget()

    assert "Daily token budget exceeded" in str(excinfo.value)

def test_ai_engine_under_budget(mock_env, monkeypatch):
    db_path, cfg_path, db, cfg = mock_env
    monkeypatch.setattr("src.config_manager.ConfigManager.get", cfg.get)

    engine = AIEngine(api_key="fake")
    db.log_ai_usage("gpt-4o", 5, 5, 10)

    # Should not raise exception
    engine.check_budget()
