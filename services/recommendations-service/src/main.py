from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

with open('data-set/mpst_full_data.json', 'r') as data:
    movies = json.load(data)

embeddings = np.load('movie_embeddings.npy')

model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/api/recommendations")
def root():
    return { "message": "Recommendations Service IS UP!" }

@app.get("/api/recommendations/search")
def search(query: str = Query(..., description="Text to search for similar movies")):
    query_embedding = model.encode([query])[0]

    similarities = cosine_similarity([query_embedding], embeddings)[0]

    top_indices = np.argsort(similarities)[::-1][:10]

    recommended_movies = [movies[i] for i in top_indices]

    return {"recommendations": recommended_movies}
