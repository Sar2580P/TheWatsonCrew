import os
from api.thewatsoncrew.Intelligence.utils.misc_utils import pr, logger
from api.thewatsoncrew.Intelligence.utils.llm_utils import Settings
import chromadb
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

class Vec_Store(VectorStoreIndex):
    def __init__(self):
        pass
    
    @classmethod
    def get_vectorstore(cls, path:str, is_ephemeral:bool = False)-> VectorStoreIndex:
        if is_ephemeral:
            chroma_client = chromadb.EphemeralClient()
            chroma_collection = chroma_client.create_collection("quickstart")
        else:
            if not os.path.exists(path):
                logger.debug(f'Creating a new vec_store : {path}')
                os.makedirs(path, exist_ok=True)
            db = chromadb.PersistentClient(path=path)
            chroma_collection = db.get_or_create_collection("quickstart")
            
        # storage_context = StorageContext.from_defaults(
            
        # )
        vector_store= ChromaVectorStore(chroma_collection = chroma_collection)


        index = VectorStoreIndex.from_vector_store(
            show_progress = True ,
            embed_model= Settings.embed_model ,
            vector_store = vector_store
        )
        
        return index
    