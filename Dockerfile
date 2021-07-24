FROM python:3

WORKDIR /home/emil/Projects/elastic_simple_engine

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 5000/tcp

CMD ["python3", "-v", "-u", "entry.py"]
