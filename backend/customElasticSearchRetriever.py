"""Wrapper around Elasticsearch"""
from __future__ import annotations

import json
from typing import Any, Iterable, List

from langchain.docstore.document import Document
from langchain.schema import BaseRetriever


class CustomElasticSearchRetriever(BaseRetriever):
    """Wrapper around Elasticsearch
    """

    size: int

    def __init__(self, client: Any, index_name: str, size=300, number=2):
        self.client = client
        self.index_name = index_name
        self.size = size
        self.number = number

    @classmethod
    def create(
            cls, elasticsearch_url: str, index_name: str
    ) -> CustomElasticSearchRetriever:
        raise NotImplementedError

    def add_texts(
            self,
            texts: Iterable[str],
            refresh_indices: bool = True,
    ) -> List[str]:
        raise NotImplementedError

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

        # print(res)

        docs = []
        for r in res["hits"]["hits"]:
            doc = Document(page_content=json.dumps(r["highlight"]["SearchableText"]))
            doc.metadata["source"] = r["_source"]["path"]["path"].replace("/inwiportal", "https://inwi-rue.bghw.de")
            docs.append(doc)
        return docs


    async def aget_relevant_documents(self, query: str) -> List[Document]:
        raise NotImplementedError
