from chunking.chunk import process_pdf_to_chunks
from ingestion.ingest import ingest
from retriever.retrievechunks import retrieve_chunks
from vectorstore.cleanup import deletecollections
from ChatModel.bot import answergenerator
import json

# ingest()
# pdf_path = "D:/signal/data/nasa_systems_engineering_handbook_0.pdf"

# process_pdf_to_chunks(pdf_path)
# deletecollections()



def convert_obj_to_json(chunks):
    retrieved_chunks = []
    for obj in chunks.objects:
        chunk = {
        "uuid": str(obj.uuid),
        "properties": obj.properties,
        "metadata": vars(obj.metadata),
    }
    retrieved_chunks.append(chunk)
    chunks_json = json.dumps(retrieved_chunks, indent=2, default=str)
    return chunks_json


if __name__ == '__main__':
    que = input('ask questions')
    chunks = retrieve_chunks(que)
    context = convert_obj_to_json(chunks)
    response = answergenerator(que,context)
    print(response)