


from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def index():
    return {'status': 'OK'}







# must be many rows at the moment