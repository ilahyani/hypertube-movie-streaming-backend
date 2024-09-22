from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get('/')
def root():
    return { 'message': 'User Service is LIIIVE' }

handler = Mangum(app)