import pytest
from unittest.mock import patch
import sys
import os

# Ensure project directory is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper

def test_fetch_reddit_posts_403_fallback():
    """Verify that fetch_reddit_posts falls back to DDG search when HTTP 403 occurs."""
    class MockResponse:
        def __init__(self, status_code, text="Blocked"):
            self.status_code = status_code
            self.text = text
        def json(self):
            raise ValueError("Not JSON")

    # Mock the direct httpx GET request to return 403
    with patch("httpx.get") as mock_get:
        mock_get.return_value = MockResponse(403)
        
        # Mock the DDG fallback to return a test post
        with patch("scraper.fetch_reddit_posts_ddg_fallback") as mock_fallback:
            mock_fallback.return_value = [{
                "title": "Fallback Post",
                "selftext": "This is from DDG",
                "url": "https://reddit.com/r/SideProject/comments/123",
                "subreddit": "SideProject"
            }]
            
            posts = scraper.fetch_reddit_posts("productivity", subreddit="SideProject")
            
            # Assert fallback was called
            mock_fallback.assert_called_once_with("productivity", "SideProject", 15)
            assert len(posts) == 1
            assert posts[0]["title"] == "Fallback Post"

def test_fetch_reddit_posts_ddg_fallback_logic():
    """Verify ddg fallback returns the formatted posts."""
    # Mock DDGS text query results
    mock_results = [
        {
            "title": "DDG Title 1",
            "body": "DDG Body 1",
            "href": "https://www.reddit.com/r/SideProject/comments/abc/title1/"
        },
        {
            "title": "Non-Reddit Title",
            "body": "Non-Reddit Body",
            "href": "https://example.com/not-reddit"
        }
    ]
    
    with patch("ddgs.DDGS") as mock_ddgs:
        # Mock the context manager __enter__
        mock_instance = mock_ddgs.return_value
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.text.return_value = mock_results
        
        posts = scraper.fetch_reddit_posts_ddg_fallback("test", "SideProject")
        
        # Verify it filtered non-Reddit URLs and mapped correctly
        assert len(posts) == 1
        assert posts[0]["title"] == "DDG Title 1"
        assert posts[0]["url"] == "https://www.reddit.com/r/SideProject/comments/abc/title1/"
        assert posts[0]["subreddit"] == "SideProject"
