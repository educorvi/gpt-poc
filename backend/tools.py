import json
from typing import Callable

from langchain.tools import Tool

import typesense

from customTypesenseRetriever import CustomTypesenseRetriever
from customElasticSearchRetriever import CustomElasticSearchRetriever
import elasticsearch


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
