"""Wrapper around Elasticsearch"""
from __future__ import annotations

import json
import urllib.parse
from typing import Any, List

from langchain.docstore.document import Document


class CustomElasticSearchRetriever:
    """Wrapper around Elasticsearch
    """

    size: int
    client: Any
    index_name: str
    number: int

    def __init__(self, client: Any, index_name: str, size=300, number=2):
        self.client = client
        self.index_name = index_name
        self.size = size
        self.number = number

    def get_relevant_documents(self, query: str) -> List[Document]:
        query_dict = {
            "from": 0,
            "size": self.number,
            "query": {"match": {"SearchableText": query}},
            "highlight": {
                "fragment_size": self.size,
                "fields": {
                    "SearchableText": {"type": "plain"}
                }
            }
        }
        res = self.client.search(index=self.index_name, body=query_dict)

        docs = []
        for r in res["hits"]["hits"]:
            doc = Document(page_content=json.dumps(r["highlight"]["SearchableText"]))
            doc.metadata["source"] = urllib.parse.quote(r["_source"]["path"]["path"])
            doc.metadata["title"] = r["_source"]["Title"]
            docs.append(doc)
        return docs
