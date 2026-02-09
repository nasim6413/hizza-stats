FROM python:3.13.0

WORKDIR /hizza-stats

COPY cogs cogs/
COPY services services/
COPY utils utils/
COPY .env .
COPY hizza-stats.py .
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

CMD ["python3", "hizza-stats.py"]