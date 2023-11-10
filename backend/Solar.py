from typing import Optional, List, Any

from langchain.callbacks.manager import CallbackManagerForLLMRun

from langchain.llms import HuggingFaceEndpoint
from typing import Any, Sequence

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage, FunctionMessage, ChatMessage, BaseMessage


class Solar(HuggingFaceEndpoint):
    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        new_prompt = '### User:\n' + prompt
        return super()._call(new_prompt, stop, run_manager, **kwargs)


def get_buffer_string_solar(
        messages: Sequence[BaseMessage], human_prefix: str = "Human", ai_prefix: str = "AI"
) -> str:
    """Convert sequence of Messages to strings and concatenate them into one string.

    Args:
        messages: Messages to be converted to strings.
        human_prefix: The prefix to prepend to contents of HumanMessages.
        ai_prefix: THe prefix to prepend to contents of AIMessages.

    Returns:
        A single string concatenation of all input messages.

    Example:
        .. code-block:: python

            from langchain.schema import AIMessage, HumanMessage

            messages = [
                HumanMessage(content="Hi, how are you?"),
                AIMessage(content="Good, how are you?"),
            ]
            get_buffer_string(messages)
            # -> "Human: Hi, how are you?\nAI: Good, how are you?"
    """
    string_messages = []
    for m in messages:

        if isinstance(m, AIMessage):
            message = '### User:\n' + m.content
        elif isinstance(m, SystemMessage):
            message = '### System:\n' + m.content
        else:
            message = '### Assistant:\n' + m.content
        string_messages.append(message)

    return '\n'.join(string_messages)


class SolarHistory(ConversationBufferMemory):
    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        if self.return_messages:
            return self.chat_memory.messages
        else:
            return get_buffer_string_solar(
                self.chat_memory.messages
            )
