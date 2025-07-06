import pytest
from unittest import mock
import app.vector_store as vector_store

def test_add_documents_to_collection_adds_docs():
    docs = [
        {"id": "1", "text": "doc1", "metadata": {"foo": "bar"}},
        {"id": "2", "text": "doc2", "metadata": {"foo": "baz"}},
    ]
    mock_collection = mock.Mock()
    count = vector_store.add_documents_to_collection(docs, collection=mock_collection)
    assert count == 2
    mock_collection.add.assert_called_once()
    args, kwargs = mock_collection.add.call_args
    assert kwargs["ids"] == ["1", "2"]
    assert kwargs["documents"] == ["doc1", "doc2"]
    assert kwargs["metadatas"] == [{"foo": "bar"}, {"foo": "baz"}] 