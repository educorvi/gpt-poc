#!/usr/bin/env python3
import argparse
import asyncio
import json
import re

import websockets
import yaml
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import get_openai_callback, StdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFaceEndpoint
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
from DB_Classes import *
from WebsocketCallbackHandler import WebsocketCallbackHandler, StreamingWebsocketHandler

from tools import create_elastic_tool


def start_backend():
    print(f"Cost of usage for the current month thus far: {round(get_cost_of_current_month() * 100) / 100}$")
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
            provider = data["provider"]
            if provider is None:
                raise Exception("No provider specified")
            if not (provider == "openai" or provider == "huggingface"):
                raise Exception("Provider not supported")
            if provider == "openai":
                open_ai_key = data["OpenAI"]["API_KEY"]
                if open_ai_key is None:
                    raise Exception("No OpenAI key specified")
                open_ai_model = data["OpenAI"]["model"]["main"]
                if open_ai_model is None:
                    raise Exception("No OpenAI main model specified")
            if provider == "huggingface":
                huggingface_key: str = data["HuggingFace"]["API_KEY"]
                if huggingface_key is None:
                    raise Exception("No HuggingFace key specified")
                endpoint: str = data["HuggingFace"]["endpoint"]
                if endpoint is None:
                    raise Exception("No HuggingFace endpoint specified")
            limit = data["monthly_limit"]
            if limit is None:
                raise Exception("No monthly limit specified")
            source_replace = data["source_replace"]
            if source_replace is None:
                raise Exception("Source replace is not specified")
            sr_from = source_replace["from"]
            sr_to = source_replace["to"]
            if sr_from is None or sr_to is None:
                raise Exception("Source replace is not fully specified")
            sr_exp = re.compile(sr_from)

            parser = argparse.ArgumentParser(prog='gpt-poc-backend',
                                             description='Backend for the chatgpt proof of concept')
            parser.add_argument('-m', '--model', help='Select the openai model, that the chatbot should use')
            parser.add_argument('-p', '--port', help='Port that the backend will run on')
            args = parser.parse_args()

            if args.model is not None:
                open_ai_model = args.model

            if args.port is not None:
                port = args.port

            async def respond(websocket):
                sources = []
                tool = create_elastic_tool(es_url, es_index, es_result_size, es_result_number, sources)

                memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                db_entry = Chat.create()

                tools = [
                    tool
                ]

                handler = WebsocketCallbackHandler(websocket, verbose=True)

                if provider == "openai":
                    model = ChatOpenAI(
                        temperature=0, openai_api_key=open_ai_key,
                        model_name=open_ai_model,
                        # streaming=True,
                        # callbacks=[StreamingWebsocketHandler(websocket)]
                    )
                else:
                    model = HuggingFaceEndpoint(
                        endpoint_url=endpoint,
                        huggingfacehub_api_token=huggingface_key,
                        model_kwargs={"temperature": 0.1, "max_new_tokens": 2000},
                        task="text-generation",
                        # callbacks=[StreamingWebsocketHandler(websocket)],
                    )
                # model = HuggingFacePipeline.from_model_id(
                #     model_id="OpenAssistant/falcon-7b-sft-mix-2000",
                #     task="text-generation",
                #     model_kwargs={"temperature": 0, "max_length": 16000, "trust_remote_code": True},
                #     callbacks=[StreamingWebsocketHandler(websocket)],
                #     device=-1
                # )

                agent = initialize_agent(
                    tools,
                    model,
                    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
                    verbose=True,
                    memory=memory,
                    callbacks=[handler]
                )
                try:
                    with get_openai_callback() as cb:
                        async for message in websocket:
                            if (get_cost_of_current_month() >= limit):
                                await websocket.send(
                                    json.dumps({"type": "message", "content": "The monthly limit has been reached."}))
                                continue
                            prompt = message + "\n Antworte auf Deutsch verwende lediglich die gegeben Informationen. Belege deine Aussagen, indem du sie mit dem Index (beginnend mit 1) der Quelle versiehst, aus der die Information stammt, z.B.: 'Dies ist ein belegtes Beispiel [1].'"
                            try:
                                task = asyncio.create_task(asyncio.to_thread(agent.run, prompt, callbacks=[handler]))
                                await task
                                result = task.result()
                                if len(sources) > 0:
                                    result += "\n\nGefundene Informationen:"
                                    index = 1
                                    while len(sources) > 0:
                                        s = sources.pop(0)
                                        result += f"\n- [{index}] [{s['title']}]({sr_exp.sub(sr_to, s['source'])})"
                                        index += 1
                            except Exception as e:
                                result = "Ein Fehler ist aufgetreten"
                                print(e)
                            await websocket.send(json.dumps({"type": "message", "content": result}))
                            await websocket.send(json.dumps({
                                "type": "usage",
                                "content": {
                                    "tokens": {
                                        "total": cb.total_tokens,
                                        "prompt": cb.prompt_tokens,
                                        "completion": cb.completion_tokens
                                    },
                                    "cost": cb.total_cost,
                                    "successful_requests": cb.successful_requests
                                }
                            }))
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
