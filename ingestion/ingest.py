from vectorstore.vectordb import client
import json

collection = client.collections.use("NasaHandbook")

def ingest():
    with collection.batch.fixed_size(batch_size=100) as batch:
        with open("D:/I2eRAGSolutionFInal/chunking/chunks.jsonl") as jsonl_file:
            for line in jsonl_file:
                print("inside the file")
                json_parsed = json.loads(line)
                batch.add_object(
                    properties={
                        "content": json_parsed["content"],
                        "section": json_parsed["section"],
                        "title": json_parsed["title"],
                        "path": json_parsed["path"],
                        "references": json_parsed["references"],
                        # add other properties as needed
                    }
                    # Weaviate will auto-vectorize based on the configured vectorizer
                )
                if batch.number_errors > 10:
                    print("Batch import stopped due to excessive errors.")
                    break

    failed_objects = collection.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")