from vectorstore.vectordb import client
from weaviate.classes.query import Rerank, MetadataQuery





def retrieve_chunks(query:str):
    jeopardy = client.collections.use("NasaHandbook")
    response = jeopardy.query.hybrid(query=query,limit=10,target_vector="MasterVector",rerank=Rerank(prop="content",query=query),return_metadata=MetadataQuery(score=True))
    return response


    
    
    