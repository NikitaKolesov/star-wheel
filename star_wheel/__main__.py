import uvicorn
from starlette.middleware.cors import CORSMiddleware

from star_wheel.handlers import app

origins = ["http://f55d6373.eu.ngrok.io", "https://f55d6373.eu.ngrok.io"]

app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
