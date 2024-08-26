from typing import Mapping, Any, Generator, Optional
from pydantic import Field
from llama_index.core.llms import CustomLLM, CompletionResponse, LLMMetadata
from llama_index.core.llms.callbacks import llm_completion_callback
from ibm_watson_machine_learning.foundation_models import Model
import os

class IBMGraniteLLM(CustomLLM):
    model_id: str = "ibm/granite-13b-chat-v2"
    context_window: int = 2048
    num_output: int = 200

    credentials: Mapping[str, str] = Field(...)
    gen_parms: Mapping[str, int] = Field(...)
    project_id: str = Field(...)
    ibm_llm: Optional[Model] = None  # Define ibm_llm as an optional attribute

    def __init__(self, credentials: Mapping[str, str], gen_parms: Mapping[str, int], project_id: str):
        super().__init__(credentials=credentials, gen_parms=gen_parms, project_id=project_id)
        self.ibm_llm = Model(self.model_id, credentials, gen_parms, project_id)

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_id,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = self.ibm_llm.generate_text(prompt)
        return CompletionResponse(text=response)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> Generator[CompletionResponse, None, None]:
        response = self.ibm_llm.generate_text(prompt)
        accumulated_response = ""
        for token in response:
            accumulated_response += token
            yield CompletionResponse(text=accumulated_response, delta=token)

if __name__=='__main__':
    # Usage
    gen_parms = {
        "MIN_NEW_TOKENS": 1,
        "MAX_NEW_TOKENS": 200
    }
    credentials = {
        "url": "https://us-south.ml.cloud.ibm.com",
        "apikey": os.getenv("cloud_apikey"),
    }

    project_id = os.environ["PROJECT_ID"]

    # Initialize the IBM Granite LLM with the given parameters
    ibm_llm = IBMGraniteLLM(credentials=credentials, gen_parms=gen_parms, project_id=project_id)

    # Example usage
    response = ibm_llm.complete("Write a poem on Sri Krishna")
    print(response.text)
