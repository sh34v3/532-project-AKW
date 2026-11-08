import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

PORT = int(os.getenv("PORT", 4000))
CONTAINER_ID = os.getenv("CONTAINER_ID", "???")

is_healthy = False


## Fast API allows us to have startup logic that executes.
## I'm using it here to build in some simulated startup delay.
@app.on_event("startup")
async def startup_event():
    global is_healthy
    print(f"container {CONTAINER_ID} init...")
    
    # Simulate heavy initialization
    await asyncio.sleep(1)  

    is_healthy = True
    print(f"container {CONTAINER_ID} init complete")


@app.get("/health")
async def status():
    print("health endpoint called")

    if is_healthy:
        return JSONResponse(status_code=200, content={"status": "ok"})
    else:
        return JSONResponse(status_code=503, content={"status": "unhealthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT)