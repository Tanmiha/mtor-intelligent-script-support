from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/reset")
def reset():
    return JSONResponse({"status": "reset successful"})