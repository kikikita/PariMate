FROM python:3.10

COPY ./requirements.txt requirements.txt

RUN python -m pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /src

COPY . /src

ENTRYPOINT [ "python3", "bot/main.py"]