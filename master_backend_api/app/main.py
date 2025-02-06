from fastapi import FastAPI

app = FastAPI(debug=True)


@app.get("/")
def index():
    return {"status": "OK"}
