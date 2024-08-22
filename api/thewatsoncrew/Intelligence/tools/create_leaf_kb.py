from api.thewatsoncrew.Intelligence.utils.llm_utils import Settings
from api.thewatsoncrew.Intelligence.node_processing.ingestion import Pipeline

# Function to take user input for source and name
def get_user_input():
    source = input("Enter the source file (e.g., 'diabetes.txt'): ")
    name = input("Enter the name for the vectordb : ")
    return source, name

# Get user input
source, name = get_user_input()

# Create a pipeline instance and ingest data
pipeline = Pipeline()
pipeline.ingest_webdata_to_vecdb(path=f'api/thewatsoncrew/Intelligence/data_sources/web_links/{source}', name=name)

# Get LLM stats
print(Settings.llm.get_stats())
