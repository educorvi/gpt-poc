"""Wrapper around Typesense"""
from __future__ import annotations

import json
import urllib.parse
from typing import Any, List

from langchain.docstore.document import Document


class CustomTypesenseRetriever:
    """Wrapper around Typesense
    """

    size: int
    number: int
    collection: str
    client: Any

    def __init__(self, client: Any, collection: str, size=300, number=2):
        self.client = client
        self.collection = collection
        self.size = size
        self.number = number

    def get_relevant_documents(self, query: str) -> List[Document]:
        docs = []

        res = self.client.collections[self.collection].documents.search({
            'q': query,
            'query_by': 'text',
            'per_page': self.number,
            'limit_hits': self.number,
            'highlight_affix_num_tokens': self.size
        })
        for r in res['hits']:
            doc = Document(page_content=json.dumps(r["highlight"]))
            doc.metadata["source"] = urllib.parse.quote(r["document"]["path"])
            doc.metadata["title"] = r["document"]["title"]
            docs.append(doc)
        # for r in res["hits"]["hits"]:
        #     doc = Document(page_content=json.dumps(r["highlight"]["SearchableText"]))
        #     doc.metadata["source"] = urllib.parse.quote(r["_source"]["path"]["path"])
        #     doc.metadata["title"] = r["_source"]["Title"]
        #     docs.append(doc)
        return docs
