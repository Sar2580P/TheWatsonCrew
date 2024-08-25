from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from dotenv import load_dotenv, find_dotenv
import os
from llama_index.embeddings.gemini import GeminiEmbedding
from typing import List, Optional, Any, Sequence
import time
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
import tiktoken
from llama_index.core.bridge.pydantic import Field
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.base.llms.types import CompletionResponse
from llama_index.llms.gemini.utils import (
    chat_from_gemini_response,
    chat_message_to_gemini,
    completion_from_gemini_response
)
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
)
from llama_index.core.utilities.gemini_utils import merge_neighboring_same_role_messages
load_dotenv(find_dotenv()) # read local .env file
from Intelligence.utils.misc_utils import pr
from ibm_watson_machine_learning.foundation_models import Model
from Intelligence.utils.watson_llm import IBMGraniteLLM

from langchain_ibm import WatsonxLLM

from langchain_google_genai import ChatGoogleGenerativeAI

llm_lc = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0.2,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    # other params...
)
model_id = "ibm/granite-13b-chat-v2"
parameters = {
    "max_new_tokens": 100,
    "min_new_tokens": 1,
    "temperature": 0.2,
    "top_k": 50,
    "top_p": 1,
}

ibm_llm_lc = WatsonxLLM(
    model_id=model_id,
    url="https://us-south.ml.cloud.ibm.com",
    project_id=os.environ["PROJECT_ID"],
    params=parameters,
    apikey=os.getenv("cloud_apikey"),
)

llm = Gemini(model_name="models/gemini-1.5-flash", api_key=os.getenv("GEMINI_API_KEY"))
Settings.llm = llm
gen_parms = {
    "MIN_NEW_TOKENS": 10,
    "MAX_NEW_TOKENS": 200
}
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": os.getenv("cloud_apikey"),
}
ibm_llm = IBMGraniteLLM(credentials=credentials, gen_parms=gen_parms, project_id=os.environ["PROJECT_ID"])

# embedding model
model_name = "models/embedding-001"
embed_model = GeminiEmbedding(
    model_name=model_name, api_key=os.getenv("GEMINI_API_KEY")
)
Settings.embed_model = embed_model

