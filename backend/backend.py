#!/usr/bin/env python3
import argparse
import asyncio
import json
import re
from typing import Any

import websockets
import yaml
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI, ChatOllama
from langchain.llms import Ollama
from DB_Classes import *
from MistralAIHistory import MistralAIHistory, get_buffer_string_mistral
from WebsocketCallbackHandler import WebsocketCallbackHandler, StreamingWebsocketHandler
from MistralAI import MistralAI
from PromptTemplates import searchQueryPromptMistral, mainTemplateMistral

from tools import create_elastic_tool, create_typesense_tool, create_qdrant_tool

import deepl


def translate_if_source_lang(translator, message, source_lang) -> str:
    if source_lang is None or translator is None:
        return message
    return translator.translate_text(message, target_lang=source_lang).text


def start_backend():
    parser = argparse.ArgumentParser(prog='gpt-poc-backend',
                                     description='Backend for the chatgpt proof of concept')
    parser.add_argument('-m', '--model', help='Select the openai model, that the chatbot should use')
    parser.add_argument('-p', '--port', help='Port that the backend will run on')
    parser.add_argument('-s', '--search-engine', help='elasticsearch or typesense')
    parser.add_argument('-c', '--config', help='path to the config file', default="/etc/gpt-poc/conf.yaml")
    args = parser.parse_args()
    # print(args)

    print(f"Cost of usage for the current month thus far: {round(get_cost_of_current_month() * 100) / 100}$")
    with open(args.config, "r") as stream:
        try:
            data = yaml.safe_load(stream)
            deepl_api_key = None
            if "DeepL" in data:
                deepl_api_key = data["DeepL"]["API_KEY"]
            translator = None
            if deepl_api_key is not None:
                translator = deepl.Translator(deepl_api_key)

            port = data["Websocket"]["port"]
            if port is None:
                raise Exception("No port specified")
            se = data["SearchEngine"]
            if args.search_engine is not None:
                se = args.search_engine
            if se is None:
                raise Exception("No search engine specified")
            if se == "qdrant":
                pass
            else:
                raise Exception("Search engine not supported")

            provider = data["provider"]
            if provider is None:
                raise Exception("No provider specified")
            if not (provider == "openai" or provider == "huggingface" or provider == "ollama"):
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
            if provider == "ollama":
                ollama_model: str = data["Ollama"]["model"]

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

            if args.model is not None:
                open_ai_model = args.model

            if args.port is not None:
                port = args.port

            async def respond(websocket):
                sources = []
                if se == "qdrant":
                    tool = create_qdrant_tool("entwicklung.educorvi.de", 6333, "inwi_pages_and_files_metadata_and_splittet",
                                              "T-Systems-onsite/cross-en-de-roberta-sentence-transformer", sources)
                else:
                    raise Exception("Search engine not supported")

                memory = MistralAIHistory(memory_key="chat_history", return_messages=True)
                db_entry = Chat.create()

                tools = [
                    tool
                ]

                handler = StreamingWebsocketHandler(websocket)
                # handler = WebsocketCallbackHandler(websocket)
                if provider == "openai":
                    model = ChatOpenAI(
                        temperature=0, openai_api_key=open_ai_key,
                        model_name=open_ai_model,
                        # streaming=True,
                        callbacks=[handler]
                    )
                elif provider == "huggingface":
                    model = MistralAI(
                        endpoint_url=endpoint,
                        huggingfacehub_api_token=huggingface_key,
                        model_kwargs={"temperature": 0.1, "max_new_tokens": 500},
                        task="text-generation",
                        # callbacks=[StreamingWebsocketHandler(websocket)],
                    )
                elif provider == "ollama":
                    model = Ollama(
                        model=ollama_model,
                        callbacks=[handler],
                        temperature=0
                    )
                try:
                    with get_openai_callback() as cb:
                        async for message in websocket:
                            source_lang = None
                            if translator is not None:
                                trans = translator.translate_text(message, target_lang="DE")
                                message = trans.text
                                source_lang = trans.detected_source_lang

                            if get_cost_of_current_month() >= limit:
                                await websocket.send(
                                    json.dumps({"type": "message",
                                                "content": f"{translate_if_source_lang(translator, 'Das monatliche Limit wurde erreicht. Bitte wende dich an den Administrator.', source_lang)}"}))
                                continue

                            # Zitiere deine Aussagen, indem du sie mit dem Index (beginnend mit 1) der Quelle versiehst, aus der die Information stammt, z.B.: 'Dies ist ein zitiertes Beispiel [i].'
                            try:




                                context = tool.func(message)
                                print(context)
                                await websocket.send(
                                    json.dumps({"type": "event", "content": {"event": "tool_end", "data": data}}))
                                mainPrompt = mainTemplateMistral.format(question=message, context=context, history=get_buffer_string_mistral(memory.chat_memory.messages))
                                print(mainPrompt)
                                result = model.invoke(mainPrompt)
                                result = translate_if_source_lang(translator, result, source_lang)
                                if len(sources) > 0:
                                    result += f"\n\n{translate_if_source_lang(translator, 'Gefundene Informationen:', source_lang)}"
                                    index = 1
                                    while len(sources) > 0:
                                        s = sources.pop(0)
                                        result += f"\n- [{index}] [{s['title']}]({sr_exp.sub(sr_to, s['source'])})"
                                        index += 1

                                memory.chat_memory.add_user_message(message)
                                memory.chat_memory.add_ai_message(result)
                            except Exception as e:
                                result = translate_if_source_lang(translator, "Es ist ein Fehler aufgetreten.",
                                                                  source_lang)

                                print(e.with_traceback())
                            await websocket.send(json.dumps({"type": "message",
                                                             "content": result}))
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
