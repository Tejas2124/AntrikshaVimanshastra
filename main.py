from chunking.chunk import process_pdf_to_chunks
from ingestion.ingest import ingest
from retriever.retrievechunks import retrieve_chunks
from vectorstore.cleanup import deletecollections

# ingest()
# pdf_path = "D:/signal/data/nasa_systems_engineering_handbook_0.pdf"

# process_pdf_to_chunks(pdf_path)
# deletecollections()

chunks = retrieve_chunks("List four system design processes in NRP")

for chunk in chunks.objects:
    print("="*25)
    print(chunk.properties['content'])
    print(chunk.metadata.score)
    print(chunk.metadata.rerank_score)
    print(chunk.properties)
    print("="*25)
    
        #     print(chunk['properties'])
        #     print(chunk['metadata'])
        #     print(chunk['properties']['content'])
