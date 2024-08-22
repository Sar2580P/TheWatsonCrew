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
    completion_from_gemini_response,
)
from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
)
from llama_index.core.utilities.gemini_utils import merge_neighboring_same_role_messages
from llama_index.core.prompts import PromptTemplate
load_dotenv(find_dotenv()) # read local .env file
from Intelligence.utils.misc_utils import pr
from Intelligence.retrieval_response.templates import translation_template


# langchain utilities for llm
from langchain_google_genai import ChatGoogleGenerativeAI
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=os.getenv("GEMINI_API_KEY"))



class Delayed_LLM(Gemini):
    sleep_time: Optional[int] = Field(description="To keep check on requests per minute rate to API calls")
    request_ct: Optional[str] = Field(description="To count total API calls made in entire query processing")
    latency: Optional[str] = Field(description="To get total time taken to get all the responses from API calls")
    last_request_time: Optional[str] = Field(description="To keep track of time the last request was made")
    def __init__(self, model_name="models/gemini-pro", api_key=os.getenv("GEMINI_API_KEY"), temperature=0.1, rpm = 50):
        
        super().__init__(model_name=model_name , api_key=api_key, temperature=temperature)
        self.sleep_time = round(60/rpm, 4) + 0.001
        self.last_request_time = 0
        self.request_ct = 0
        self.latency = 0
        
        
    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        
        if self.sleep_time- (time.time() - self.last_request_time) > 0:
            time.sleep(self.sleep_time - (time.time() - self.last_request_time))
        
        start = time.time()
        result = self._model.generate_content(prompt, **kwargs)
        result =  completion_from_gemini_response(result)
        
        self.request_ct += 1
        self.latency += round(time.time() - start, 3)
        self.last_request_time = time.time()
        
        return result
    
    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        if self.sleep_time- (time.time() - self.last_request_time) > 0:
            time.sleep(self.sleep_time - (time.time() - self.last_request_time))
            
        start = time.time()
        merged_messages = merge_neighboring_same_role_messages(messages)
        *history, next_msg = map(chat_message_to_gemini, merged_messages)
        chat = self._model.start_chat(history=history)
        response = chat.send_message(next_msg)
        answer =  chat_from_gemini_response(response)
        
        self.request_ct +=1
        self.latency += round(time.time() - start, 3)
        self.last_request_time = time.time()
        return answer
    
    def reset(self):
        self.request_ct = 0
        self.latency = 0
        
    def get_stats(self):
        pr.green(f"{'-'*100}")
        pr.green(f"Total API calls made : {self.request_ct}")
        pr.green(f"Latency : {self.latency} seconds")
    
Settings.llm = Delayed_LLM(model_name="models/gemini-pro", api_key=os.getenv("GEMINI_API_KEY"))

#_____________________________________________________________________________________________________________________________
model_name = "models/embedding-001"
class Delayed_Embedding(GeminiEmbedding):
    sleep_time: Optional[str] = Field(description="To reduce the requests per minute rate to API calls")
    request_ct: Optional[str] = Field(description="To count total API calls made in entire query processing")
    response_time: Optional[str] = Field(description="To get total time taken to get all the responses from API calls")
    embed_batch_size: int = Field(description="To keep track of batch size for embedding", default=20)
    def __init__(self, model_name: str = "models/embedding-001", api_key: Optional[str] = None, sleep_time = 0.7):
        super().__init__(model_name=model_name, api_key=api_key)
        self.request_ct = 0
        self.response_time = 0
        self.sleep_time = sleep_time
        
        
    def _get_text_embedding(self, text: str) -> List[float]:
        start = time.time()
        embedded_text =  self._model.embed_content(
            model=self.model_name,
            content=text,
            title=self.title,
            task_type=self.task_type,
        )["embedding"]
        self.request_ct += 1
        self.response_time += round(time.time() - start, 3)
        return embedded_text

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        return  [self._get_text_embedding(text)
                        for text in texts]
        
    
    def reset(self):
        self.request_ct = 0
        self.response_time = 0

Settings.embed_model = Delayed_Embedding(model_name=model_name, api_key=os.getenv("GEMINI_API_KEY")) #embed_dim : 768

#_____________________________________________________________________________________________________________________________
     
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5").encode
)
Settings.callback_manager = CallbackManager([token_counter])

#______________________________________________________________________________________________________________________________

def use_llm(x):
    response = Settings.llm.complete(x)
    return response.text, response.additional_kwargs

def translate(content, lang):
    translation_prompt = PromptTemplate(translation_template).partial_format(lang = lang, original_content = content)                                                      
    response = Settings.llm.complete(translation_prompt)
    return response.text

def embed(x):
    return Settings.embed_model.get_text_embedding(x)


# template = "Statement : {statement}\n ----------------------------\n\n\
# INSTRUCTIONS : \nYou need to do NER in above text into tags like : ['Disease', 'Medicine' , 'Anatomical_Region'] and return a list containing tuple of (NER-type , name, anatomical_description in < 6 words)\n \
#     \nstart : index of starting letter of word\nend : index of last letter of word  \
# Response: \n"
    
# text = '''
# The 55-year-old male patient presented with symptoms of Myocarditis and subsequently developed Atrial Fibrillation. 
# He was administered Amiodarone to manage the arrhythmia. Additionally, his history revealed Type 2 Diabetes Mellitus, 
# controlled with Metformin and occasional use of Insulin Glargine. During the examination, signs of Chronic Obstructive Pulmonary Disease (COPD) were noted, for which he was already on Tiotropium. Recently, he experienced severe joint pain attributed to Rheumatoid Arthritis, 
# being treated with Methotrexate and Etanercept. To address his Hypertension, Amlodipine and Lisinopril were prescribed. Moreover, the patient had a previous episode of Deep Vein Thrombosis (DVT), currently managed with Warfarin. In light of his persistent Gastroesophageal Reflux Disease (GERD), he was taking Omeprazole. 
# A comprehensive review of his medication regimen was essential to prevent potential drug interactions and ensure optimal therapeutic outcomes, given the complexity of his multiple chronic conditions.'''
# # prompt = template.format(statement = text)
# # print(use_llm(prompt)[0])