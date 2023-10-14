FROM python:3-slim as python
ENV PYTHONUNBUFFERED=true

RUN pip install poetry==1.6.1

WORKDIR /code
COPY . /code

RUN poetry config virtualenvs.create false &&\
    poetry install --no-interaction --no-ansi -vvv

CMD ["python", "main.py"]