from fastapi import FastAPI, Query, Request
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import json, os, time

load_dotenv()

app = FastAPI()

with open('data/top_movies_data.json', 'r') as data:
    movies = json.load(data)

embeddings = np.load('data/movie_embeddings.npy')

model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/api/recommendations")
def root():
    return { "message": "Recommendations Service IS UP!" }

@app.get("/api/recommendations/search")
async def search(request: Request,query: str = Query(..., description="Text to search for similar movies")):
    if not request.headers.get("X-User-ID"):
        return Response(status_code=403, content='Forbidden')

    query_embedding = model.encode([query])[0]
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    top_indices = np.argsort(similarities)[::-1][:10]
    matching_movies = [movies[i] for i in top_indices]

    recommendations = []
    async with httpx.AsyncClient() as client:
        for movie in matching_movies:
            try:
                response = await client.get(
                    f'{os.getenv('OMDB_API')}&i={movie.get('id')}',
                    headers = {
                        'Authorization': request.headers.get("Authorization")
                    }
                )
                if response.status_code == 200:
                    movie = response.json()
                    recommendations.append({
                    'id': movie.get('imdbID'),
                    'title': movie.get('Title'),
                    'year': movie.get('Year'),
                    'rating': movie.get('imdbRating'),
                    'thumbnail': movie.get('Poster'),
                })
                time.sleep(1)
            except Exception as e:
                print(f"Failed to fetch movie data: {e}")

    return {"recommendations": recommendations}
