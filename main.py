import uvicorn

from core.config import config


def main() -> None:
    uvicorn.run(
        "api.server:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.API_RELOAD,
    )


if __name__ == "__main__":
    main()
