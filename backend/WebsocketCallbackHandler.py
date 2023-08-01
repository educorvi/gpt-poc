import asyncio
import json
from typing import Dict, Any, List, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import BaseMessage, LLMResult, AgentAction, AgentFinish


class StreamingWebsocketHandler(BaseCallbackHandler):
    websocket: Any

    def __init__(self, websocket):
        self.websocket = websocket
        super().__init__()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        # s = asyncio.to_thread(self.websocket.send, json.dumps({"type": "message_stream", "content": token}))
        _ = asyncio.create_task(self.websocket.send(json.dumps({"type": "message_stream", "content": token})))


class WebsocketCallbackHandler(BaseCallbackHandler):
    websocket: Any
    verbose: bool

    def __init__(self, websocket, verbose: bool = False):
        self.websocket = websocket
        self.verbose = verbose
        super().__init__()

    def send_event(self, event: str, data: Any) -> None:
        # loop = asyncio.get_running_loop()
        # if loop and loop.is_running():
        #     loop.create_task(
        #         self.websocket.send(json.dumps({"type": "event", "content": {"event": event, "data": data}})))
        # else:
        #     print("No running loop found, could not send event")
        # print(json.dumps({"type": "event", "content": {"event": event}}))
        asyncio.run(self.websocket.send(json.dumps({"type": "event", "content": {"event": event, "data": data}})))

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        if self.verbose:
            print(prompts)
        self.send_event("llm_start", {"serialized": serialized, "prompts": prompts})

    def on_chat_model_start(
            self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        if self.verbose:
            print(messages)
        self.send_event("chat_model_start", {})

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        if self.verbose:
            print(response)
        self.send_event("llm_end", {})

    def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        print(error)
        self.send_event("llm_error", error)

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        self.send_event("chain_start", {})

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        self.send_event("chain_end", outputs)

    def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        print(error)
        self.send_event("chain_error", error)

    def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        self.send_event("tool_start", {"serialized": serialized, "input_str": input_str})

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        self.send_event("tool_end", output)

    def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        print(error)
        self.send_event("tool_error", error)

    def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        self.send_event("text", text)

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        self.send_event("agent_action", {"tool": action.tool, "tool_input": action.tool_input})

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        self.send_event("agent_finish", finish)
