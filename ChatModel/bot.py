from .model import chatmodel
from .prompt import ANSWERING_PRMOMT
from langchain.messages import HumanMessage
from langchain_core.prompts import PromptTemplate




def answergenerator(query,context):
    dynamic_prompt_template = PromptTemplate(
    template = ANSWERING_PRMOMT,
    input_variables = ["query", "context"])
    formatted_prompt = dynamic_prompt_template.format(
        query=query,
        context=context
    )
    inputs = [HumanMessage(content=formatted_prompt)]
    response = chatmodel.invoke(inputs)
    return response.content    

