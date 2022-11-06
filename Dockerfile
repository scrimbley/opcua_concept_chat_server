# syntax=docker/dockerfile:1
FROM alpine:latest
RUN apk add --no-cache python3 py3-pip
WORKDIR /app
COPY opcua-server.py .
RUN pip install asyncua
CMD ["python3", "opcua-server.py"]
EXPOSE 4840/tcp
