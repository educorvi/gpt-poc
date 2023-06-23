#!/usr/bin/env python3
import asyncio
import json

import websockets
import yaml
from rich.progress import track
from pathlib import Path

source_path = Path(__file__).resolve()
source_dir = source_path.parent

async def test():
    with open("/etc/gpt-poc/conf.yaml", "r") as stream:
        try:
            data = yaml.safe_load(stream)
            port = data["Websocket"]["port"]
            if port is None:
                raise Exception("No port specified")

        except yaml.YAMLError as exc:
            print(exc)

    with open(source_dir.joinpath("questions.json"), "r") as f:
        questions = json.load(f)

    results = []
    try:
        for question in track(questions, description="Answering questions..."):
            print(question, end=': ')
            websocket = await websockets.connect(f"ws://localhost:{port}")
            await websocket.send(question)
            answer = await websocket.recv()
            results.append({"question": question, "answer": answer})
            await websocket.close()
            print("Done")
    except Exception as e:
        print(e)
    with open(source_dir.joinpath("results.json"), "w") as outfile:
        json.dump(results, outfile)

if __name__ == '__main__':
    asyncio.run(test())
