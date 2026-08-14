FROM python:3.12-slim
WORKDIR /app
COPY src/mcp/pyproject.toml ./pyproject.toml
COPY src/mcp/app ./app
RUN pip install --no-cache-dir -e .
EXPOSE 8080
CMD ["python", "-m", "app.main"]
