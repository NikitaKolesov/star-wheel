import uvicorn

from star_wheel.handlers import app

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, port=8000)