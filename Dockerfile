FROM python:3.7-stretch
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT [ "python" ]
CMD [ "dumb-server.py" ]
EXPOSE 5000