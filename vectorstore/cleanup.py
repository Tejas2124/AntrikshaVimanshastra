from vectorstore.vectordb import client


def deletecollections():
    client.collections.delete("NasaHandbook")