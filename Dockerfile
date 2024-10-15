# Container image that runs your code
FROM python:3.13-alpine

# Copies your code file from your action repository to the filesystem path `/` of the container
COPY entrypoint.sh upload_package.py soti_api.py / 

RUN pip3 install requests
RUN pip3 install urllib3

# Code file to execute when the docker container starts up (`entrypoint.sh`)
ENTRYPOINT ["/entrypoint.sh"]
