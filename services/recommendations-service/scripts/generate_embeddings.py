import json
from sentence_transformers import SentenceTransformer
import numpy as np

with open('data/top_movies_data.json', 'r') as data:
    movies = json.load(data)

descriptions = [movie["plot"] for movie in movies]

model = SentenceTransformer('all-MiniLM-L6-v2')

embeddings = model.encode(descriptions)

np.save('movie_embeddings.npy', embeddings)

print("Embeddings generated and saved to movie_embeddings.npy")