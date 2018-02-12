FROM python:3-onbuild

ADD . /vin_decoder

WORKDIR /vin_decoder

# COPY startup script into known file location in container
COPY start.sh /start.sh

ENV DJANGO_ENV=prod
ENV DOCKER_CONTAINER=1

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000

# CMD specifcies the command to execute to start the server running.
CMD ["/start.sh"]
# done!