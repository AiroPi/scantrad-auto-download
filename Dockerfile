FROM python:3.10.4
WORKDIR /app
# COPY requirements.txt requirements.txt
RUN python3 -m pip install requests
RUN python3 -m pip install mloader
RUN python3 -m pip install pycryptodome
RUN python3 -m pip install tenacity
RUN python3 -m pip install mega.py --no-deps
COPY ./src/ .
CMD ["python3", "./main.py"]
