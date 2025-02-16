import json
import os
import traceback

import pinecone
from openai import OpenAI


# Test event:
# {
#   "headers": {"x-api-key": "gfdgdA"},
#   "body": {"text": "some text"}
# }


def handler(event, context):
    # in case you want to ask for the API key in the headers
    # and use e.g. lambda url as the endpoint
    # OPENAI_API_KEY = event.get("headers", {}).get("x-api-key")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    try:
        raw_body = event.get("body", "{}")
        body = json.loads(raw_body)
        input_text = body.get("text")
        if not input_text:
            raise ValueError("Missing 'text' in request body")
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": traceback.format_exc(), "body": raw_body}),
        }

    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.embeddings.create(input=input_text, model=body.get("model", "text-embedding-3-small"))
        embedding_vector = response.data[0].embedding
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Embedding generation failed", "details": str(e)}),
        }

    try:
        pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        pinecone_host = os.environ.get("PINECONE_HOST")
        pinecone_namespace = os.environ.get("PINECONE_NAMESPACE")

        pc = pinecone.Pinecone(api_key=pinecone_api_key)
        index = pc.Index(host=pinecone_host)

        query_response = index.query(
            namespace=pinecone_namespace,
            vector=list(embedding_vector),
            top_k=body.get("top_k", 10),
            include_values=False,
            include_metadata=True,
        )
        query_response = [x.to_dict() for x in query_response.matches]
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error querying Pinecone", "details": str(e)}),
        }

    return {"statusCode": 200, "body": json.dumps(query_response)}
