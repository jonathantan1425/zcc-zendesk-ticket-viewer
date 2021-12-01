FROM python:3.8-slim-buster
Maintainer Jonathan Tan Wui Heong

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

CMD ["python3", "./ticket_viewer/viewer.py"]