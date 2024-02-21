FROM python:3.11.5
WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
COPY ./.env /src/.env

RUN pip install --no-cache-dir -r /src/requirements.txt
COPY app /src/app

ENV PYTHONPATH "${PYTHONPATH}:/src/app"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]