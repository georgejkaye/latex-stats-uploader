FROM python:3.11-bookworm as builder

ARG POETRY_VERSION=1.5.1
ARG TEXCOUNT_VERSION=3.2.0.41

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install poetry==${POETRY_VERSION}

WORKDIR /app

RUN curl -L "https://app.uio.no/ifi/texcount/download.php?file=texcount_$(echo ${TEXCOUNT_VERSION} | tr . _).zip" > texcount.zip
RUN unzip texcount.zip -d texcount
RUN mv texcount/texcount.pl texcount/texcount

COPY pyproject.toml poetry.lock ./
RUN touch README.md
RUN poetry install --without dev --no-root && rm -rf ${POETRY_CACHE_DIR}

FROM python:3.11-bookworm as runtime

RUN apt update
RUN apt install pdftk -y
RUN pdftk --version

ENV VIRTUAL_ENV "/app/.venv"
ENV TEXCOUNT "/app/texcount"
ENV PATH "/app/.venv/bin:/app/texcount:$PATH"
ENV PYTHONPATH "/app/src:$PYTHONPATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder ${TEXCOUNT} ${TEXCOUNT}

WORKDIR /app

RUN chmod +x texcount/texcount

COPY src ./src

ENTRYPOINT [ "python", "/app/src/latexstats/upload.py" ]
