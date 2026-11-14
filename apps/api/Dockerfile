FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir uv && uv pip install --system .
ENV SPHEREX_CACHE_DIR=/cache
VOLUME ["/cache"]
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
