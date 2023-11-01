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

COPY pyproject.toml poetry.lock /
RUN touch README.md
RUN poetry install --without dev --no-root && rm -rf ${POETRY_CACHE_DIR}

FROM python:3.11-slim-bookworm as runtime

ENV VIRTUAL_ENV=/.venv \
    PATH="/.venv/bin:$PATH" \
    PYTHONPATH="/src:$PYTHONPATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder /pyproject.toml /pyproject.toml

COPY src /src
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
