# Use Python as the base image
FROM python:3.12

WORKDIR /app
COPY ./pyproject.toml /app/
COPY ./poetry.lock /app/
COPY ./backend /app

# Install Poetry
RUN pip install poetry

# Install dependencies using Poetry
RUN poetry install --no-root

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI backend
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
