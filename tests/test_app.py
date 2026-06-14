import pytest
from fastapi.testclient import TestClient
import os
import sys

# Ensure project directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import database
import analyzer
import scraper

client = TestClient(app)

def test_home_route():
    """Verify home page loads successfully with HTML content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Reddit Startup Demand Checker" in response.text

def test_database_initialization():
    """Verify database setup successfully runs and schema tables exist."""
    database.init_db()
    assert os.path.exists(database.DB_PATH)

def test_heuristic_analysis_empty():
    """Verify analyzer returns a structured low-demand object when no posts are provided."""
    res = analyzer.analyze_heuristics([], "test query")
    assert res["overall_score"] == 0
    assert res["interest_level"] == "None"
    assert res["volume_score"] == 0
    assert "No posts found for analysis." in res["key_pain_points"]

def test_heuristic_analysis_sample_data():
    """Verify scoring logic processes engagement and keywords correctly."""
    sample_posts = [
        {
            "title": "I hate modern startup tools",
            "selftext": "They are annoying, expensive, and struggle to solve actual problems. Excel is better.",
            "author": "user1",
            "score": 10,
            "num_comments": 5,
            "created_utc": 1600000000.0,
            "url": "https://reddit.com/r/SideProject/comments/1",
            "subreddit": "SideProject"
        },
        {
            "title": "Is there a better way to do this?",
            "selftext": "Looking for a tool that automates personal CRM workflows. Current manual methods suck.",
            "author": "user2",
            "score": 20,
            "num_comments": 15,
            "created_utc": 1600000000.0,
            "url": "https://reddit.com/r/SideProject/comments/2",
            "subreddit": "SideProject"
        }
    ]
    
    res = analyzer.analyze_heuristics(sample_posts, "personal crm")
    
    assert res["total_posts"] == 2
    assert res["overall_score"] > 0
    assert len(res["key_pain_points"]) > 0
    assert "Excel" in res["competitors_mentioned"]

def test_get_reports_empty(monkeypatch):
    """Verify reports history returns list of saved items."""
    # Mock database to return a fixed list
    def mock_get_all():
        return [{"id": 1, "idea": "Test", "keywords": "test", "overall_score": 80, "timestamp": "2026-06-15T03:00:00"}]
    
    monkeypatch.setattr(database, "get_all_reports", mock_get_all)
    
    response = client.get("/reports")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["idea"] == "Test"
