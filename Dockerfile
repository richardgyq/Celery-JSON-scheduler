# INSTALL PYTHON IMAGE
FROM python:3

# Create the group and user to be used in this container
RUN groupadd usergroup \
    && useradd -m -g usergroup -s /bin/bash appuser

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["chmod", "+x", "./run_celery.sh"]
RUN ["chmod", "+x", "./run_celery_beat.sh"]
RUN ["chmod", "+x", "./run_flower.sh"]

# timezone
ENV TZ=Canada/Pacific
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN chown -R appuser:usergroup /home/appuser
RUN chown -R appuser:usergroup /usr/src/app
USER appuser
