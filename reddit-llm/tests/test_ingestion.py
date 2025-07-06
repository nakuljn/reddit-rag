import os
import pytest
from unittest import mock

import app.ingestion as ingestion


def test_get_reddit_credentials_missing(monkeypatch):
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("REDDIT_USER_AGENT", raising=False)
    with pytest.raises(ValueError):
        ingestion.get_reddit_credentials()

def test_get_reddit_credentials_present(monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "dummy_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "dummy_secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "dummy_agent")
    creds = ingestion.get_reddit_credentials()
    assert creds["client_id"] == "dummy_id"
    assert creds["client_secret"] == "dummy_secret"
    assert creds["user_agent"] == "dummy_agent"

@mock.patch("app.ingestion.praw.Reddit")
def test_get_reddit_client(mock_reddit, monkeypatch):
    monkeypatch.setenv("REDDIT_CLIENT_ID", "dummy_id")
    monkeypatch.setenv("REDDIT_CLIENT_SECRET", "dummy_secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "dummy_agent")
    client = ingestion.get_reddit_client()
    mock_reddit.assert_called_once_with(
        client_id="dummy_id",
        client_secret="dummy_secret",
        user_agent="dummy_agent"
    )

@mock.patch("app.ingestion.get_reddit_client")
def test_fetch_top_posts_filters(mock_get_reddit_client, monkeypatch):
    # Create mock subreddit and posts
    mock_subreddit = mock.Mock()
    mock_post1 = mock.Mock()
    mock_post1.over_18 = False
    mock_post1.score = 15
    mock_post1.title = "Title 1"
    mock_post1.selftext = "Content 1"
    
    mock_post2 = mock.Mock()  # NSFW
    mock_post2.over_18 = True
    mock_post2.score = 20
    mock_post2.title = "Title 2"
    mock_post2.selftext = "Content 2"

    mock_post3 = mock.Mock()  # Low score
    mock_post3.over_18 = False
    mock_post3.score = 5
    mock_post3.title = "Title 3"
    mock_post3.selftext = "Content 3"

    mock_post4 = mock.Mock()  # No content
    mock_post4.over_18 = False
    mock_post4.score = 20
    mock_post4.title = ""
    mock_post4.selftext = ""

    mock_subreddit.top.return_value = [mock_post1, mock_post2, mock_post3, mock_post4]
    mock_reddit = mock.Mock()
    mock_reddit.subreddit.return_value = mock_subreddit
    mock_get_reddit_client.return_value = mock_reddit

    posts = ingestion.fetch_top_posts("somesubreddit", limit=10, min_score=10)
    assert len(posts) == 1
    assert posts[0].title == "Title 1"

def test_fetch_top_posts_empty_subreddit():
    with pytest.raises(ValueError, match="Subreddit name cannot be empty"):
        ingestion.fetch_top_posts("")
    
    with pytest.raises(ValueError, match="Subreddit name cannot be empty"):
        ingestion.fetch_top_posts("   ")

@mock.patch("app.ingestion.get_reddit_client")
def test_fetch_top_posts_network_error(mock_get_reddit_client):
    mock_get_reddit_client.side_effect = Exception("Network error")
    posts = ingestion.fetch_top_posts("somesubreddit")
    assert posts == []

def test_fetch_top_comments_filters():
    # Create mock post and comments
    mock_post = mock.Mock()
    mock_comment1 = mock.Mock()
    mock_comment1.stickied = False
    mock_comment1.author = mock.Mock(is_mod=False)
    mock_comment1.body = "This is a good comment."

    mock_comment2 = mock.Mock()  # Stickied
    mock_comment2.stickied = True
    mock_comment2.author = mock.Mock(is_mod=False)
    mock_comment2.body = "Stickied comment."

    mock_comment3 = mock.Mock()  # Mod comment
    mock_comment3.stickied = False
    mock_comment3.author = mock.Mock(is_mod=True)
    mock_comment3.body = "Moderator comment."

    mock_comment4 = mock.Mock()  # No body
    mock_comment4.stickied = False
    mock_comment4.author = mock.Mock(is_mod=False)
    mock_comment4.body = None

    # Properly mock the comments attribute
    mock_comments = mock.Mock()
    mock_comments.__iter__ = mock.Mock(return_value=iter([mock_comment1, mock_comment2, mock_comment3, mock_comment4]))
    mock_comments.replace_more = mock.Mock()
    mock_post.comments = mock_comments
    mock_post.comment_sort = None

    comments = ingestion.fetch_top_comments(mock_post, limit=3)
    assert comments == ["This is a good comment."]

def test_fetch_top_comments_empty_post():
    comments = ingestion.fetch_top_comments(None)
    assert comments == []

def test_fetch_top_comments_error():
    mock_post = mock.Mock()
    mock_post.comments = mock.Mock()
    mock_post.comments.replace_more.side_effect = Exception("Comment error")
    
    comments = ingestion.fetch_top_comments(mock_post)
    assert comments == []

def test_structure_post_with_comments():
    mock_post = mock.Mock()
    mock_post.title = "How to learn FastAPI?"
    mock_post.selftext = "I'm new to FastAPI. Any tips?"
    mock_post.id = "abc123"
    mock_post.score = 42
    mock_post.created_utc = 1701234567
    mock_post.url = "https://reddit.com/r/learnpython/abc123"
    mock_post.subreddit = "learnpython"
    comments = ["Start with the official docs.", "Check out YouTube tutorials."]

    doc = ingestion.structure_post_with_comments(mock_post, comments)
    assert doc["id"] == "abc123"
    assert "How to learn FastAPI?" in doc["text"]
    assert "I'm new to FastAPI. Any tips?" in doc["text"]
    assert "Top Comment 1: Start with the official docs." in doc["text"]
    assert "Top Comment 2: Check out YouTube tutorials." in doc["text"]
    assert doc["metadata"]["subreddit"] == "learnpython"
    assert doc["metadata"]["post_id"] == "abc123"
    assert doc["metadata"]["score"] == 42
    assert doc["metadata"]["created_utc"] == 1701234567
    assert doc["metadata"]["url"] == "https://reddit.com/r/learnpython/abc123"

def test_structure_post_with_comments_empty_post():
    doc = ingestion.structure_post_with_comments(None, [])
    assert doc is None

def test_structure_post_with_comments_error():
    mock_post = mock.Mock()
    mock_post.selftext = "Test content"
    mock_post.id = "test123"
    mock_post.score = 10
    mock_post.created_utc = 1701234567
    mock_post.url = "https://test.com"
    mock_post.subreddit = "test"
    
    # Make title access fail by using a property that raises an exception
    type(mock_post).title = mock.PropertyMock(side_effect=Exception("Title error"))
    
    doc = ingestion.structure_post_with_comments(mock_post, [])
    assert doc is None

@mock.patch("app.ingestion.fetch_top_posts")
def test_ingest_subreddit(mock_fetch_posts, monkeypatch):
    # Mock posts
    mock_post1 = mock.Mock()
    mock_post1.id = "p1"
    mock_post2 = mock.Mock()
    mock_post2.id = "p2"
    mock_fetch_posts.return_value = [mock_post1, mock_post2]
    
    # Mock comments
    with mock.patch("app.ingestion.fetch_top_comments") as mock_fetch_comments:
        mock_fetch_comments.side_effect = [["c1", "c2"], ["c3"]]
        
        # Mock structured docs
        with mock.patch("app.ingestion.structure_post_with_comments") as mock_structure:
            mock_structure.side_effect = [
                {"id": "p1", "text": "...", "metadata": {}},
                {"id": "p2", "text": "...", "metadata": {}}
            ]
            
            docs = ingestion.ingest_subreddit("somesubreddit", post_limit=2, comment_limit=2)
            assert len(docs) == 2
            assert docs[0]["id"] == "p1"
            assert docs[1]["id"] == "p2"
            mock_fetch_posts.assert_called_once_with("somesubreddit", limit=2, min_score=10, time_filter="week")
            mock_fetch_comments.assert_any_call(mock_post1, limit=2)
            mock_fetch_comments.assert_any_call(mock_post2, limit=2)
            assert mock_structure.call_count == 2

def test_ingest_subreddit_empty_name():
    with pytest.raises(ValueError, match="Subreddit name cannot be empty"):
        ingestion.ingest_subreddit("")
    
    with pytest.raises(ValueError, match="Subreddit name cannot be empty"):
        ingestion.ingest_subreddit("   ")

@mock.patch("app.ingestion.fetch_top_posts")
def test_ingest_subreddit_error(mock_fetch_posts):
    mock_fetch_posts.side_effect = Exception("Ingestion error")
    docs = ingestion.ingest_subreddit("somesubreddit")
    assert docs == [] 