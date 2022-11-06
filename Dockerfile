# syntax=docker/dockerfile:1
FROM alpine:latest
RUN apk update
RUN apk add --no-cache python3 py3-pip py3-virtualenv
RUN adduser -D newuser
USER newuser
WORKDIR /home/newuser
COPY --chown=newuser:newuser opcua-server.py .
RUN python3 -m venv opc_v
RUN source opc_v/bin/activate
RUN pip install asyncua
ENV PATH="/home/newuser/.local/bin:${PATH}"
CMD ["python3", "opcua-server.py"]
EXPOSE 4840/tcp
