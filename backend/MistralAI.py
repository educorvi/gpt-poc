from typing import Optional, List, Any

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms import HuggingFaceEndpoint


class MistralAI(HuggingFaceEndpoint):
    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> str:
        new_prompt = '[INST] ' + prompt + ' [/INST]'
        return super()._call(new_prompt, stop, run_manager, **kwargs)
