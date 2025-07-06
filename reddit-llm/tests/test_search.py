from unittest import mock
import app.search as search

def test_search_similar_documents_returns_expected_docs():
    mock_collection = mock.Mock()
    mock_results = {
        "ids": [["id1", "id2"]],
        "documents": [["doc1 text", "doc2 text"]],
        "metadatas": [[{"foo": "bar"}, {"foo": "baz"}]],
        "distances": [[0.1, 0.2]]
    }
    mock_collection.query.return_value = mock_results
    docs = search.search_similar_documents(
        query="test query",
        top_k=2,
        collection=mock_collection,
        embedding_fn=None
    )
    assert len(docs) == 2
    assert docs[0]["id"] == "id1"
    assert docs[0]["text"] == "doc1 text"
    assert docs[0]["metadata"] == {"foo": "bar"}
    assert docs[0]["distance"] == 0.1
    assert docs[1]["id"] == "id2"
    assert docs[1]["text"] == "doc2 text"
    assert docs[1]["metadata"] == {"foo": "baz"}
    assert docs[1]["distance"] == 0.2

def test_search_similar_documents_empty_query():
    docs = search.search_similar_documents("")
    assert docs == []
    
    docs = search.search_similar_documents("   ")
    assert docs == []

def test_search_similar_documents_empty_results():
    mock_collection = mock.Mock()
    mock_collection.query.return_value = {"ids": [], "documents": [], "metadatas": []}
    docs = search.search_similar_documents(
        query="test query",
        collection=mock_collection
    )
    assert docs == []

def test_search_similar_documents_collection_error():
    mock_collection = mock.Mock()
    mock_collection.query.side_effect = Exception("Database error")
    docs = search.search_similar_documents(
        query="test query",
        collection=mock_collection
    )
    assert docs == [] 