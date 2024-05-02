FROM python:3.11-alpine3.19

COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt

RUN apk add --no-cache tzdata

RUN crontab -l | { cat; echo "00	12	*	*	*	cd /app && python3 main.py"; } | crontab -
CMD ["crond", "-f"]
#CMD ["/bin/ash"]