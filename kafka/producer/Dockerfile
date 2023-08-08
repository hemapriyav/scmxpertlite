FROM python:3.10

WORKDIR /producer

COPY requirement.txt ./

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

EXPOSE 8000

CMD ["python", "producer.py"]