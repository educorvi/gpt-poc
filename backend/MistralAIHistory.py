from typing import Any, Sequence

from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, BaseMessage, ChatMessage, FunctionMessage, HumanMessage, SystemMessage


def get_buffer_string_mistral(
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
            message = m.content
        else:
            message = f"[INST] {m.content} [/INST]"
        string_messages.append(message)

    return f"<s>{' '.join(string_messages)}</s>"


class MistralAIHistory(ConversationBufferMemory):
    @property
    def buffer(self) -> Any:
        """String buffer of memory."""
        if self.return_messages:
            return self.chat_memory.messages
        else:
            return get_buffer_string_mistral(
                self.chat_memory.messages
            )
