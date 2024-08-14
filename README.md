# eodh-ac-api

API for interacting with Action Creator component and scheduling spatial computation in EO Data Hub.

## Getting started

Create the environment:

```shell
make env
```

Run `pre-commit` hooks:

```shell
make pc
```

## Guides

### Running the API

This section provides step-by-step instructions on how to run a FastAPI application locally.

#### Prerequisites

Before running the FastAPI application, ensure that you have the [environment configured](docs/guides/setup-dev-env.md).

#### Run the Application

You can now run the FastAPI application using Uvicorn, which is an ASGI server for Python apps:

```bash
uvicorn app:app --reload
```

- `app:app`: Refers to the `app` instance in the `main.py` file.
- `--reload`: Enables auto-reload, so the server will restart when you make changes to the code.

#### Access the Application

Once the application is running, you can access it in your web browser at:

```
http://127.0.0.1:8000
```

#### Explore the API Documentation

FastAPI automatically generates interactive API documentation. You can explore it by navigating to the following URLs:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

#### Additional Commands

- **Stopping the Server**: You can stop the server by pressing `CTRL+C` in the terminal where the server is running.

### Other guides

You can read more here:

- [Development env setup](docs/guides/setup-dev-env.md)
- [Contributing](docs/guides/contributing.md)
- [Makefile usage](docs/guides/makefile-usage.md)
- [Running tests](docs/guides/tests.md)

## Docs

To build project documentation run:

```shell
make docs
```

and then:

```shell
mkdocs serve
```
