

# index = Vec_Store.get_vectorstore(path='vector_store/medical_db')
# retriever = VectorIndexRetriever(
#     index=index,
#     similarity_top_k=7,
# )
# # assemble query engine
# query_engine = RetrieverQueryEngine(
#     retriever=retriever,
#     response_synthesizer=response_synthesizer,
# )

# from llama_index.core.agent import ReActAgent
# from llama_index.core.tools import QueryEngineTool, ToolMetadata

# query_engine_tools = [
#     QueryEngineTool(
#         query_engine=query_engine,
#         metadata=ToolMetadata(
#             name="diabetes_database",
#             description="Provides information about all information related to diabetes.",
#         ),
#     ),
# ]

# # initialize ReAct agent
# agent = ReActAgent.from_tools(query_engine_tools, llm=Settings.llm, verbose=True)
# # # query
# # response = query_engine.query("What are the types of diabetes?")
# response = agent.query('What is type-2 diabetes? Elaborate it in detail.')
# print(response)
# print('response_time : ' , Settings.llm.response_time)
# print('request_ct : ' , Settings.llm.request_ct)

# Using the emoji directly
doctor_emoji = "🧑‍⚕️"
print(doctor_emoji)
# Using Unicode code points
