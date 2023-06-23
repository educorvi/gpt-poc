import json

from langchain.tools import Tool

from customElasticSearchRetriever import CustomElasticSearchRetriever
import elasticsearch


def create_elastic_tool(elasticsearch_url, elasticsearch_index, result_size, result_number):
    retriever = CustomElasticSearchRetriever(elasticsearch.Elasticsearch(elasticsearch_url),
                                             elasticsearch_index, result_size, result_number)

    def search_documents(query: str) -> str:
        results = retriever.get_relevant_documents(query)
        ret_string = "\n--------------------------------------------------------------------\n".join(
            list(map(lambda d: "Metadata: \n" + json.dumps(d.metadata) + "\nContent: \n" + d.page_content,
                     results))
        )
        return ret_string

    return Tool(
        name="ElasticSearch",
        func=search_documents,
        description="useful for when you need to answer questions about everything related to health and safety, the DGUV and most other things. The Contents are in German and the search has to be done in german as well. This tool provides access to an elasticsearch index, so formulate your query accordingly."
    )
