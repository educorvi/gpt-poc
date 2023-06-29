#!/usr/bin/env python3
import asyncio
import json

import websockets
import yaml
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from DB_Classes import *

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
            es_result_number = data["ElasticSearch"]["result_number"]
            es_result_size = data["ElasticSearch"]["result_size"]
            if es_url is None or es_index is None or es_result_size is None or es_result_number is None:
                raise Exception("ElasticSearch config incomplete")
            open_ai_key = data["OpenAI"]["API_KEY"]
            if open_ai_key is None:
                raise Exception("No OpenAI key specified")
            open_ai_model = data["OpenAI"]["model"]["main"]
            if open_ai_model is None:
                raise Exception("No OpenAI main model specified")
            tool = create_elastic_tool(es_url, es_index, es_result_size, es_result_number)

            async def respond(websocket):
                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                db_entry = Chat.create()

                tools = [
                    tool
                ]

                agent = initialize_agent(tools, ChatOpenAI(temperature=0, openai_api_key=open_ai_key,
                                                           model_name=open_ai_model),
                                         agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                                         verbose=True,
                                         memory=memory)
                try:
                    with get_openai_callback() as cb:
                        async for message in websocket:
                            prompt = message + "\n Antworte auf Deutsch und gebe die Quellen an, aus denen du Informationen bezogen hast. Gebe als Quellen ausschließlich die URLs an, die vom Elasticsearch tool unter 'Metadata.source' angegeben werden. Gebe Quellen als Markdown Liste an im folgenden Format: \"[Name der Quelle](URL der Quelle)\""
                            try:
                                result = agent.run(prompt)
                            except Exception as e:
                                result = "Ein Fehler ist aufgetreten"
                                print(e)
                            await websocket.send(json.dumps({"type": "message", "content": result}))
                            await websocket.send(json.dumps({"type": "usage", "content": {"tokens": {"total": cb.total_tokens, "prompt": cb.prompt_tokens, "completion": cb.completion_tokens}, "cost": cb.total_cost, "successful_requests": cb.successful_requests}}))
                            db_entry.cost = cb.total_cost
                            db_entry.tokens = cb.total_tokens
                            db_entry.save()
                except websockets.exceptions.ConnectionClosedError:
                    print("Connection closed")

            async def run_websocket(port_number):
                async with websockets.serve(respond, "0.0.0.0", port_number):
                    print(f"Started websocket server on port", port_number)
                    await asyncio.Future()

            asyncio.run(run_websocket(port))
        except yaml.YAMLError as exc:
            print(exc)
