FROM python:3

LABEL author="Sergey Makov"
LABEL description="HeadHunter vacancies parser"

WORKDIR /app

COPY . /app

RUN pip install -r /app/requirements.txt

RUN rm requirements.txt
