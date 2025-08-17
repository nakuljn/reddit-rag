import os
from dotenv import load_dotenv
import praw

# Load environment variables from .env if present
load_dotenv()

def get_reddit_credentials():
    """Return Reddit API credentials as a dict."""
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "reddit-llm-ingester/0.1")
    if not (client_id and client_secret and user_agent):
        raise ValueError("Missing Reddit API credentials in environment variables.")
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "user_agent": user_agent,
    }

def get_reddit_client():
    """Initialize and return a PRAW Reddit client using environment credentials."""
    creds = get_reddit_credentials()
    reddit = praw.Reddit(
        client_id=creds["client_id"],
        client_secret=creds["client_secret"],
        user_agent=creds["user_agent"]
    )
    return reddit

def fetch_top_posts(subreddit_name, limit=100, min_score=10, time_filter="week"):
    """
    Fetch top posts from a subreddit, filtering out NSFW, low-score, or empty-content posts.
    Returns a list of praw.models.Submission objects.
    """
    if not subreddit_name or not subreddit_name.strip():
        raise ValueError("Subreddit name cannot be empty")
    
    try:
        reddit = get_reddit_client()
        subreddit = reddit.subreddit(subreddit_name)
        posts = []
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            if post.over_18:
                continue  # Skip NSFW
            if post.score < min_score:
                continue  # Skip low-score
            if not post.title:
                continue  # Skip posts with no title
            posts.append(post)
        return posts
    except Exception as e:
        print(f"Failed to fetch posts from r/{subreddit_name}: {str(e)}")
        return []

def fetch_top_comments(post, limit=3):
    """
    Fetch the top N user comments (by score) for a given PRAW Submission (post).
    Skips stickied and moderator comments. Returns a list of comment bodies.
    """
    if not post:
        return []
    
    try:
        # Ensure comments are loaded and sorted by score
        post.comment_sort = "top"
        post.comments.replace_more(limit=0)
        comments = []
        for comment in post.comments:
            if getattr(comment, 'stickied', False):
                continue
            if getattr(comment, 'author', None) and getattr(comment.author, 'is_mod', False):
                continue
            if not getattr(comment, 'body', None):
                continue
            comments.append(comment.body)
            if len(comments) >= limit:
                break
        return comments
    except Exception as e:
        print(f"Failed to fetch comments for post {getattr(post, 'id', 'unknown')}: {str(e)}")
        return []

def structure_post_with_comments(post, comments):
    """
    Combine a post and its comments into a structured document dict.
    """
    if not post:
        return None
    
    try:
        combined_text = f"Title: {post.title}\n\n"
        if post.selftext:
            combined_text += f"Post: {post.selftext}\n\n"
        else:
            combined_text += "Post: [No text content]\n\n"
        for i, comment in enumerate(comments, 1):
            combined_text += f"Top Comment {i}: {comment}\n\n"
        doc = {
            "id": f"{post.id}",
            "text": combined_text.strip(),
            "metadata": {
                "subreddit": str(getattr(post, "subreddit", "unknown")),
                "post_id": str(post.id),
                "score": int(post.score),
                "created_utc": int(post.created_utc),
                "url": str(post.url),
            },
        }
        return doc
    except Exception as e:
        print(f"Failed to structure post {getattr(post, 'id', 'unknown')}: {str(e)}")
        return None

def ingest_subreddit(subreddit_name, post_limit=100, comment_limit=3, min_score=10, time_filter="week"):
    """
    Ingest a subreddit: fetch top posts, their top comments, and structure as documents.
    Returns a list of document dicts.
    """
    if not subreddit_name or not subreddit_name.strip():
        raise ValueError("Subreddit name cannot be empty")
    
    try:
        posts = fetch_top_posts(subreddit_name, limit=post_limit, min_score=min_score, time_filter=time_filter)
        docs = []
        for post in posts:
            comments = fetch_top_comments(post, limit=comment_limit)
            doc = structure_post_with_comments(post, comments)
            if doc:  # Only add valid documents
                docs.append(doc)
        return docs
    except Exception as e:
        print(f"Failed to ingest subreddit r/{subreddit_name}: {str(e)}")
        return []

def ingest_multiple_subreddits(subreddits, post_limit=10, comment_limit=2, min_score=5, time_filter="week"):
    """Ingest multiple subreddits and return combined documents."""
    all_docs = []
    for subreddit in subreddits:
        print(f"\n--- Ingesting r/{subreddit} ---")
        docs = ingest_subreddit(subreddit, post_limit, comment_limit, min_score, time_filter)
        print(f"Fetched {len(docs)} documents from r/{subreddit}")
        all_docs.extend(docs)
    return all_docs

def main():
    import sys
    from app.vector_store import add_documents_to_collection
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single subreddit: python -m app.ingestion <subreddit> [post_limit] [comment_limit] [min_score] [time_filter]")
        print("  Multiple subreddits: python -m app.ingestion <subreddit1,subreddit2,subreddit3> [post_limit] [comment_limit] [min_score] [time_filter]")
        print("\nExamples:")
        print("  python -m app.ingestion python 10 2 5 week")
        print("  python -m app.ingestion python,MachineLearning,datascience 5 2 10 month")
        print("  python -m app.ingestion askreddit,todayilearned,explainlikeimfive 20 3 50 week")
        sys.exit(1)
    
    subreddit_input = sys.argv[1]
    post_limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    comment_limit = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    min_score = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    time_filter = sys.argv[5] if len(sys.argv) > 5 else "week"
    
    if ',' in subreddit_input:
        subreddits = [s.strip() for s in subreddit_input.split(',')]
        print(f"Ingesting {len(subreddits)} subreddits: {', '.join([f'r/{s}' for s in subreddits])}")
        print(f"Parameters: posts={post_limit}, comments={comment_limit}, min_score={min_score}, time_filter={time_filter}")
        docs = ingest_multiple_subreddits(subreddits, post_limit, comment_limit, min_score, time_filter)
    else:
        subreddit = subreddit_input
        print(f"Ingesting r/{subreddit} (posts={post_limit}, comments={comment_limit}, min_score={min_score}, time_filter={time_filter})...")
        docs = ingest_subreddit(subreddit, post_limit, comment_limit, min_score, time_filter)
    
    print(f"\nTotal documents fetched: {len(docs)}")
    print("Storing in ChromaDB...")
    added = add_documents_to_collection(docs)
    print(f"✅ Stored {added} documents in ChromaDB.")

if __name__ == "__main__":
    main()
