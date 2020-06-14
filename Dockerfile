FROM python:3.7-stretch
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT [ "python" ]
CMD [ "dumb-server.py" ]
EXPOSE 5000