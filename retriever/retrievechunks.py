from vectorstore.vectordb import client
from weaviate.classes.query import Rerank, MetadataQuery





def retrieve(query:str):
    jeopardy = client.collections.use("NasaHandbook")
    response = jeopardy.query.hybrid(query=query,limit=10,rerank=Rerank(prop=),return_metadata=MetadataQuery(score=True))
    return response

for o in response.objects:
    print(o.properties)