from langchain_groq.chat_models import ChatGroq
from dotenv import load_dotenv
load_dotenv()



chatmodel = ChatGroq(model='openai/gpt-oss-120b')