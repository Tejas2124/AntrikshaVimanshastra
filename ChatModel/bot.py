from model import chatmodel
from prompt import ANSWERING_PRMOMT
from langchain.messages import HumanMessage
from langchain_core.prompts import PromptTemplate




def answergenerator(query,context):
    dynamic_prompt_template = PromptTemplate(
    template = ANSWERING_PRMOMT,
    input_variables = ["query", "context"])
    inputs = {"messages": [HumanMessage(content=dynamic_prompt_template)]}
    response = chatmodel.invoke(inputs)
    return response    

