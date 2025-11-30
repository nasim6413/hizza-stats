FROM python:3.10.12

WORKDIR /hizza-stats

COPY cogs cogs/
COPY models models/
COPY utils utils/
COPY .env .
COPY hizza-stats.py .
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

CMD ["python3", "hizza-stats.py"]