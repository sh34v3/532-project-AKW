import os
import asyncio
import pika
import json
import random
import time
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

PORT = int(os.getenv("PORT", 4000))
CONTAINER_ID = os.getenv("CONTAINER_ID", "???")
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")



is_healthy = False
rabbit_connection = None
rabbit_channel = None



## STARTUP EVENT --------------------
## Fast API allows us to have startup logic that executes.
## I'm using it here to connect to RabbitMQ and simulate some extra startup delay
@app.on_event("startup")
async def startup_event():
    global is_healthy
    global rabbit_connection
    global rabbit_channel
    print(f"container {CONTAINER_ID} init...")
    
    # Simulate heavy initialization
    await asyncio.sleep(1)  

    # Retry loop to wait for RabbitMQ to become available
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempting to connect to RabbitMQ at {RABBITMQ_HOST} (Attempt {attempt}/{max_retries})...")
            
            # Establish blocking connection to RabbitMQ
            params = pika.ConnectionParameters(host=RABBITMQ_HOST)
            rabbit_connection = pika.BlockingConnection(params)
            rabbit_channel = rabbit_connection.channel()
            
            # 
            rabbit_channel.queue_declare(queue='mod-jobs', durable=True)
            
            print("Successfully connected to RabbitMQ and declared queue!")
            break
        except pika.exceptions.AMQPConnectionError as e:
            if attempt == max_retries:
                print("Max connection retries reached. RabbitMQ connection failed.")
                raise e
            print(f"RabbitMQ not ready yet. Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

    is_healthy = True
    print(f"container {CONTAINER_ID} init complete")

## ENDPOINTS --------------------



@app.post("/submit_job")
async def submit_job():
    print("submit-job endpoint called")

    global rabbit_channel, rabbit_connection
    
    # Verify the RabbitMQ connection is active
    if not rabbit_channel or not rabbit_connection or not rabbit_connection.is_open:
        return JSONResponse(
            status_code=503, 
            content={"status": "error", "message": "RabbitMQ connection not available"}
        )

    try: 
        id = abs(hash(f"{int(time.time() * 1000)}-{int(random.random() * 100000)}"))

        job_payload = {
                "task-id": id,
                "source": f"container-{CONTAINER_ID}"
            }

        # Publish the message to the queue
        rabbit_channel.basic_publish(
            exchange='',       
            routing_key='mod-jobs', 
            body=json.dumps(job_payload),
            properties=pika.BasicProperties(
                delivery_mode=2,      # Make message persistent (survives broker restarts)
            )
        )

        # Success response
        print(f"Successfully published job to 'mod-jobs': {job_payload}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success", 
                "message": "Job submitted to mod-jobs", 
                "job": job_payload
            }
        )

    except Exception as e:
        # Failure response
        print(f"Failed to publish job: {e}")
        return JSONResponse(
            status_code=500, 
            content={"status": "error", "message": str(e)}
        )




@app.get("/health")
async def health():
    print("health endpoint called")

    rabbit_is_up = rabbit_connection and rabbit_connection.is_open

    if is_healthy and rabbit_is_up:
        return JSONResponse(status_code=200, content={"status": "ok", "rabbitmq": "connected"})
    else:
        return JSONResponse(status_code=503, content={"status": "unhealthy", "rabbitmq": "disconnected" })



## SHUTDOWN EVENT --------------------
@app.on_event("shutdown")
def shutdown_event():
    global rabbit_connection
    if rabbit_connection and rabbit_connection.is_open:
        rabbit_connection.close()
        print("Closed RabbitMQ connection safely.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=PORT)
