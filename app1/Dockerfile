FROM crossbario/autobahn-python:cpy3-alpine

RUN pip install requests
COPY . /app

CMD  ["python", "-u", "app.py"]
