FROM python:3.9-slim
EXPOSE 8501
USER root
RUN mkdir /opt/carbon_app
RUN chmod -R 777 /opt/carbon_app
WORKDIR /opt/carbon_app
COPY requirements.txt requirements.txt
COPY project_contents project_contents
RUN apt-get update
RUN apt-get -y install gcc
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
VOLUME /w210containermount

ENTRYPOINT ["streamlit", "run", "project_contents/app/Home.py", "--server.port=8501", "--server.address=0.0.0.0"]