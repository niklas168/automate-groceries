# Use Python as the base image
FROM python:3.12

WORKDIR /frontend
COPY ./frontend /frontend
COPY ./pyproject.toml /frontend/
COPY ./poetry.lock /frontend/

RUN pip install poetry
RUN poetry install --no-root

EXPOSE 8765

CMD ["poetry", "run", "solara", "run", "sol.py", "--host", "0.0.0.0", "--port", "8765"]
