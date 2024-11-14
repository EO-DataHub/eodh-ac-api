FROM python:3.11-slim-bullseye

ENV CONDA_ENV=notebook \
    # Tell apt-get to not block installs by asking for interactive human input
    DEBIAN_FRONTEND=noninteractive \
    # Use /bin/bash as shell, not the default /bin/sh (arrow keys, etc don't work then)
    SHELL=/bin/bash \
    # Setup locale to be UTF-8, avoiding gnarly hard to debug encoding errors
    LANG=C.UTF-8  \
    LC_ALL=C.UTF-8

# Install basic apt packages
RUN echo "Installing Apt-get packages..." \
    && apt-get update --fix-missing > /dev/null \
    && apt-get install -y apt-utils wget build-essential graphviz graphviz-dev zip tzdata proj-bin > /dev/null \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code

EXPOSE 8000

CMD ["fastapi", "run", "app.py", "--port", "8000"]
