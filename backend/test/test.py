#!/usr/bin/env python3
import asyncio
import json
import time
import os

import websockets
import yaml
from rich.progress import track
from pathlib import Path
from datetime import datetime

source_path = Path(__file__).resolve()
source_dir = source_path.parent


async def test():
    with open("/etc/gpt-poc/conf.yaml", "r") as stream:
        try:
            data = yaml.safe_load(stream)
            port = data["Websocket"]["port"]
            if port is None:
                raise Exception("No port specified")
            open_ai_model = data["OpenAI"]["model"]["main"]
            es_result_number = data["ElasticSearch"]["result_number"]
            es_result_size = data["ElasticSearch"]["result_size"]

        except yaml.YAMLError as exc:
            print(exc)

    with open(source_dir.joinpath("questions.json"), "r") as f:
        questions = json.load(f)

    results = []
    try:
        for question in track(questions, description="Answering questions..."):
            websocket = await websockets.connect(f"ws://localhost:{port}")
            await websocket.send(question)
            start = time.time()
            answer = json.loads(await websocket.recv())
            usage = json.loads(await websocket.recv())
            end = time.time()
            results.append({"question": question, "answer": answer, "usage": usage, "execution_duration_seconds": end - start})
            await websocket.close()
            print(f"\u2713 {question} ({round((end-start)*1000)}ms)")
    except Exception as e:
        print(e)

    if not os.path.exists(source_dir.joinpath("results").joinpath(open_ai_model)):
        os.makedirs(source_dir.joinpath("results").joinpath(open_ai_model))

    now = datetime.now()

    dt_string = now.strftime("%d-%m-%Y_%H:%M")
    with open(source_dir.joinpath("results").joinpath(open_ai_model).joinpath(f"{dt_string}.json"), "w") as outfile:
        output = {
            "meta": {
                "model": open_ai_model,
                "elastic_search": {
                    "result_number": es_result_number,
                    "result_size": es_result_size
                },
                "date": str(now)
            },
            "results": results
        }
        json.dump(output, outfile)

    with open(source_dir.joinpath("results").joinpath(open_ai_model).joinpath(f"{dt_string}.md"), "w") as outfile:
        output = f'''
# Evaluation
## Meta
- Datum: {now.strftime("%d.%m.%Y %H:%M")}
- Model: {open_ai_model}
- ElasticSearch:
    - Anzahl der Ergebnisse: {es_result_number}
    - Größe der Ergebnisse: {es_result_size}
- Durchschnittliche Antwortzeit: {round(sum(map(lambda r: r["execution_duration_seconds"], results)) / len(results) * 1000)}ms
- Gesamtkosten: {round(sum(map(lambda r: r["usage"]["content"]["cost"], results))*100)/100}$
        
## Ergebnisse
        
'''
        for result in results:
            output += f'''
### {result["question"]}
{result["answer"]["content"]}

Meta:      
- Antwortzeit: {round(result["execution_duration_seconds"] * 1000)/1000}s
- Kosten: {round(result["usage"]["content"]["cost"]*100)/100}$
'''

        outfile.write(output)


if __name__ == '__main__':
    asyncio.run(test())
