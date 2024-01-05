import asyncio
import json
from typing import Dict, Any, List, Union

from langchain.callbacks.base import BaseCallbackHandler, AsyncCallbackHandler
from langchain.schema import BaseMessage, LLMResult, AgentAction, AgentFinish


class WebsocketCallbackHandler(AsyncCallbackHandler):
    websocket: Any

    def __init__(self, websocket):
        self.websocket = websocket
        super().__init__()

    async def send_event(self, event: str, data: Any) -> None:
        if event == "message_stream":
            print(data, end="")
        else:
            print("\n"+event)
        await self.websocket.send(json.dumps({"type": "event", "content": {"event": event, "data": data}}))



    async def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        await self.send_event("llm_start", {"serialized": serialized, "prompts": prompts})

    async def on_chat_model_start(
            self, serialized: Dict[str, Any], messages: List[List[BaseMessage]], **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        await self.send_event("chat_model_start", {})

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> Any:
        """Run when LLM ends running."""
        await self.send_event("llm_end", {})

    async def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when LLM errors."""
        await self.send_event("llm_error", str(error))

    async def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        await self.send_event("chain_start", {})

    async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> Any:
        """Run when chain ends running."""
        await self.send_event("chain_end", outputs)

    async def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        await self.send_event("chain_error", str(error))

    async def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> Any:
        """Run when tool starts running."""
        await self.send_event("tool_start", {"serialized": serialized, "input_str": input_str})

    async def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        await self.send_event("tool_end", output)

    async def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> Any:
        """Run when tool errors."""
        await self.send_event("tool_error", str(error))

    async def on_text(self, text: str, **kwargs: Any) -> Any:
        """Run on arbitrary text."""
        await self.send_event("text", text)

    async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        await self.send_event("agent_action", {"tool": action.tool, "tool_input": action.tool_input})

    async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> Any:
        """Run on agent end."""
        await self.send_event("agent_finish", finish)


class StreamingWebsocketHandler(WebsocketCallbackHandler):
    websocket: Any

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> Any:
        """Run on new LLM token. Only available when streaming is enabled."""
        # s = asyncio.to_thread(self.websocket.send, json.dumps({"type": "message_stream", "content": token}))
        await self.send_event("message_stream", token)
