from weaviate.classes.config import Configure, Property, DataType
from vectordb import client



client.collections.create(
    "NasaHandbook",
    properties=[
        Property(name="content", data_type=DataType.TEXT),
        Property(name="section", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="path", data_type=DataType.TEXT),
        Property(name="page", data_type=DataType.INT),
        Property(name="references",data_type=DataType.OBJECT_ARRAY),
        Property(name="chunk_id", data_type=DataType.TEXT),

    ],
    vector_config=[
        Configure.Vectors.text2vec_weaviate(
            name="MasterVector",
            source_properties=["content","section","title","path","references"],  # or add "content" if you want it vectorized too
            model="Snowflake/snowflake-arctic-embed-l-v2.0",
        )
    ],
)