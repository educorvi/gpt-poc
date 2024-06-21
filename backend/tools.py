import json
from typing import Callable
from langchain_huggingface import (HuggingFaceEmbeddings)

import typesense

from customTypesenseRetriever import CustomTypesenseRetriever
from customElasticSearchRetriever import CustomElasticSearchRetriever
import elasticsearch

import qdrant_client

from qdrant_client.http import models
from langchain_qdrant import Qdrant
from langchain_core.tools import Tool


def search_documents(get_documents_func: Callable[[str], list[any]], sources: list) -> Callable[[str], str]:
    def func(query: str) -> str:
        results = get_documents_func(query)
        sources.extend(list(map(lambda d: {'source': d.metadata["source"], 'title': d.metadata["title"]}, results)))
        ret_string = "\n--------------------------------------------------------------------\n".join(
            list(map(lambda d: "Metadata: \n" + json.dumps(d.metadata) + "\nContent: \n" + d.page_content,
                     results))
        )
        return ret_string

    return func


def create_elastic_tool(elasticsearch_url, elasticsearch_index, result_size, result_number, sources: list):
    retriever = CustomElasticSearchRetriever(elasticsearch.Elasticsearch(elasticsearch_url),
                                             elasticsearch_index, result_size, result_number)

    return Tool(
        name="ElasticSearch",
        func=search_documents(retriever.get_relevant_documents, sources),
        description="useful for when you need to answer questions about everything related to health and safety, the DGUV and most other things. The Contents are in German and the search has to be done in german as well. This tool provides access to an elasticsearch index, so formulate your query accordingly."
    )


def create_typesense_tool(host: str, port: str, protocol: str, api_key: str, collection: str, result_size,
                          result_number, sources: list):
    client = typesense.Client({
        'api_key': api_key,
        'nodes': [
            {
                'host': host,
                'port': port,
                'protocol': protocol
            }
        ]
    })
    retriever = CustomTypesenseRetriever(client, collection, result_size, result_number)

    return Tool(
        name="Typesense",
        func=search_documents(retriever.get_relevant_documents, sources),
        description="useful for when you need to answer questions about everything related to health and safety, the DGUV and most other things. The Contents are in German and the search has to be done in german as well. This tool provides access to a typesense index, so formulate your query accordingly.")


def create_qdrant_tool(host, port, collection, embeddings_model_name, api_key, sources: list):
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    q = qdrant_client.QdrantClient(host=host, port=port, api_key=api_key, https=False)
    qclient = Qdrant(
        client=q,
        embeddings=embeddings,
        collection_name=collection,
        content_payload_key="text",
        metadata_payload_key='metadata'
    )

    def search_documents_qdrant(query: str) -> str:
        filter=models.Filter(
                must_not=[
                    models.FieldCondition(key="text", match=models.MatchValue(value=""))
                ]
            )
        results = qclient.similarity_search(query, filter=filter, k=8)
        print(list(map(lambda d: d.metadata, results)))
        sources.extend(list(map(lambda d: {'source': d.metadata.get("url"), 'title': d.metadata.get("title")}, results)))
        ret_string = "\n--------------------------------------------------------------------\n".join(
            list(map(lambda d: "Number: "+str(results.index(d)+1)+"\nMetadata: \n" + json.dumps(d.metadata) + "\nContent: \n" + d.page_content,
                     results))
        )
        return ret_string

    return Tool(
        name="Qdrant",
        func=search_documents_qdrant,
        description="useful for when you need to answer questions about everything related to health and safety, the DGUV and most other things. The Contents are in German and the search has to be done in german as well. This tool provides access to a qdrant index, so formulate your query accordingly."
    )


