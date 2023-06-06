FROM python:alpine

ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install ipython gunicorn waitress

CMD python app.py