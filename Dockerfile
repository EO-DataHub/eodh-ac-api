FROM python:3.13-slim-bullseye

ENV DEBIAN_FRONTEND=noninteractive \
    # Use /bin/bash as shell, not the default /bin/sh (arrow keys, etc don't work then)
    SHELL=/bin/bash \
    # Setup locale to be UTF-8, avoiding gnarly hard to debug encoding errors
    LANG=C.UTF-8  \
    LC_ALL=C.UTF-8

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install basic apt packages
RUN echo "Installing apt-get packages..." \
    && apt-get update --fix-missing > /dev/null \
    && apt-get install -y apt-utils wget build-essential cwltool graphviz graphviz-dev zip tzdata proj-bin > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./uv.lock /code
COPY ./pyproject.toml /code

RUN uv sync --frozen --no-cache

COPY . /code

EXPOSE 8000

CMD [".venv/bin/python3", "-m", "fastapi", "run", "app.py", "--port", "8000"]
