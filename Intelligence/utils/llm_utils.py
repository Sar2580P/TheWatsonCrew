from llama_index.core import Settings
from dotenv import load_dotenv, find_dotenv
import os
from llama_index.embeddings.gemini import GeminiEmbedding
load_dotenv(find_dotenv()) # read local .env file
from Intelligence.utils.watson_llm import IBMGraniteLLM

from langchain_ibm import WatsonxLLM
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
gen_parms = {
    "MIN_NEW_TOKENS": 10,
    "MAX_NEW_TOKENS": 200
}
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": os.getenv("cloud_apikey"),
}
ibm_llm = IBMGraniteLLM(credentials=credentials, gen_parms=gen_parms, project_id=os.environ["PROJECT_ID"])
Settings.llm = ibm_llm
# embedding model
model_name = "models/embedding-001"
embed_model = GeminiEmbedding(
    model_name=model_name, api_key=os.getenv("GEMINI_API_KEY")
)
Settings.embed_model = embed_model

