import uvicorn

from star_wheel.handlers import app


def main():
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    uvicorn.run(app, port=8000)


if __name__ == "__main__":
    main()
