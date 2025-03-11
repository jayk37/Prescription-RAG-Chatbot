# backend/query_search.py
from fuzzysearch import find_near_matches
from openai import OpenAI
from chunks_to_chromadb import get_embedding, create_drug_collection
import os
from groq import Groq

# api_res = {
#     "base_url": "http://localhost:1234/v1",
#     "api_key": "lm-studio"
# }

# client = OpenAI(**api_res)
# model = "llama-3.2-3b-instruct"

client = Groq(
    api_key="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",
)
model = "llama-3.2-3b-preview"
def generate(prompt, context=None, instruction=None):
    if context:
        context = f"context : {context}\n"
    else:
        context = ""
    if instruction:
        instruction = f"{instruction}\n"
    else:
        instruction = "base on the prompt give output"
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": f"prompt : {prompt}"}
        ],
        temperature=0.7,
    )
    
    res = completion.choices[0].message.content
    return res

def search_fuzzy(query, data, max_l_dist=3):
    query_lower = query.lower()
    results = []
    for doc in data:
        if isinstance(doc, str):
            doc_lower = doc.lower()
            matches = find_near_matches(query_lower, doc_lower, max_l_dist=max_l_dist)
            if matches:
                results.append(doc)
    print("Fuzzy Search results:", results)
    return results

def search_semantic(query, collection, top_k=5):
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    semantic_results = results["documents"][0] if "documents" in results else []
    print("Semantic Search results:", semantic_results)
    return semantic_results

def retrieve_relevant_chunks(query_text, collection, top_k=5, max_l_dist=3):
    # Get semantic search results (assuming they are sorted by relevance)
    semantic_results = search_semantic(query_text, collection, top_k=top_k)
    
    # Get all documents from the collection
    all_docs = collection.get()["documents"]
    
    # Perform fuzzy search with a stricter threshold
    fuzzy_results = search_fuzzy(query_text, all_docs, max_l_dist=max_l_dist)
    
    # Prioritize semantic results, then append fuzzy results that are not already present
    # combined = semantic_results + [doc for doc in fuzzy_results if doc not in semantic_results]
    combined = [doc for doc in fuzzy_results]
    # Limit the final result to top_k items
    combined = combined[:top_k]
    
    logs = (
        f"Semantic Results: {semantic_results}\n"
        f"Fuzzy Results (max_l_dist={max_l_dist}): {fuzzy_results}\n"
        f"Combined Results: {combined}"
    )



    context = f"{logs}\nCombined Data: {combined}"


    final_response = generate(query_text, context=context, instruction="Generate a final, comprehensive answer using the provided context and query.")
    
    return final_response

    # return combined, logs
