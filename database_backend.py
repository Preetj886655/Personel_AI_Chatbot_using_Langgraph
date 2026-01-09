from langgraph.graph import StateGraph,START,END
from langchain_core.output_parsers import JsonOutputParser
from typing import TypedDict,Literal,Annotated
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
import os
from langchain_core.messages import BaseMessage,HumanMessage
# c:\Users\preet.DESKTOP-U4TQ2OD\Downloads\langgraph_tutorial\myvenv\Lib\site-packages\langchain_core\_api\deprecation.py:26: UserWarning: Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.
from pydantic.v1.fields import FieldInfo as FieldInfoV1
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
# from .autonotebook import tqdm as notebook_tqdm
os.environ['HUGGINGFACEHUB_API_TOKEN']="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"
llm=HuggingFaceEndpoint(
    repo_id='deepseek-ai/DeepSeek-V3.2',
    task='text-generation'
) 
conn=sqlite3.connect(database='chatbot.db',check_same_thread=False)

model=ChatHuggingFace(llm=llm)
from langgraph.graph.message import add_messages 

class chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
def chat_node(state:chatstate):
 prompt=state['messages']
 res=model.invoke(prompt).content
 return {'messages':[res]}
checkpointer=SqliteSaver(conn=conn)
graph=StateGraph(chatstate)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

workflow=graph.compile(checkpointer=checkpointer)

   

def retrive_all_threads():
   all_thread=set()
   for checkpoint in checkpointer.list(None):
      all_thread.add(checkpoint.config['configurable']['thread_id'])
      return list(all_thread)




# res=model.invoke("what is largest holy river in india").content
# thread_id='1'
# while True:
#     prompt=input("enter the message")
#     print('Human Messagae:',prompt)
#     if prompt=="exit":
#         break 
#     config={'configurable':{'thread_id':thread_id}}
#     res=workflow.invoke({"messages":[HumanMessage(content=prompt)]},config=config)
#     print("the AI Message is -",res['messages'][-1].content)