FROM python:3.11-bookworm as builder

ARG TEXCOUNT_VERSION=3.2.0.41
ARG POETRY_VERSION=1.5.1

RUN curl -L "https://app.uio.no/ifi/texcount/download.php?file=texcount_$(echo ${TEXCOUNT_VERSION} | tr . _).zip" > texcount.zip
RUN unzip texcount.zip

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --without dev --no-root && rm -rf ${POETRY_CACHE_DIR}

FROM python:3.11-slim-bookworm as runtime

RUN apt update
RUN apt install git -y

ENV VIRTUAL_ENV "/app/.venv"
ENV PATH "/app/.venv/bin:$PATH"
ENV PYTHONPATH "/app/src:$PYTHONPATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app

COPY src ./src

ENTRYPOINT [ "python", "/app/src/latexstats/upload.py" ]
