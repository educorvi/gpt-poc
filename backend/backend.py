#!/usr/bin/env python3
import asyncio

import websockets
import yaml
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage

from tools import create_elastic_tool

def start_backend():
    with open("/etc/gpt-poc/conf.yaml", "r") as stream:
        try:
            data = yaml.safe_load(stream)
            port = data["Websocket"]["port"]
            if port is None:
                raise Exception("No port specified")
            es_url = data["ElasticSearch"]["url"]
            es_index = data["ElasticSearch"]["index"]
            es_result_size = data["ElasticSearch"]["result_size"]
            if es_url is None or es_index is None or es_result_size is None:
                raise Exception("ElasticSearch config incomplete")
            open_ai_key = data["OpenAI"]["API_KEY"]
            if open_ai_key is None:
                raise Exception("No OpenAI key specified")
            tool = create_elastic_tool(es_url, es_index, es_result_size)


            async def respond(websocket):
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                formatter = ChatOpenAI(temperature=0, openai_api_key=open_ai_key)

                tools = [
                    tool
                ]

                agent = initialize_agent(tools, ChatOpenAI(temperature=0, openai_api_key=open_ai_key),
                                         agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                                         verbose=True,
                                         memory=memory)
                async for message in websocket:
                    prompt = message + "\n Antworte auf Deutsch und gebe Quellen an. Gebe als Quellen ausschließlich die URLs an, die vom Elasticsearch tool unter 'Metadata.source' angegeben werden."

                    try:
                        result = formatter([HumanMessage(
                            content=f"format the following text as HTML\n{agent.run(prompt)}")]).content
                    except Exception as e:
                        result = "Ein Fehler ist aufgetreten"
                        print(e)
                    # tokens += cb.total_tokens
                    await websocket.send(result)


            async def run_websocket(port_number):
                async with websockets.serve(respond, "0.0.0.0", port_number):
                    print(f"Started websocket server on port", port_number)
                    await asyncio.Future()


            asyncio.run(run_websocket(port))
        except yaml.YAMLError as exc:
            print(exc)
