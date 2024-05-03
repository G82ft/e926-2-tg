FROM python:3.11-alpine3.19

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt
RUN apk add --no-cache tzdata # && apk add nano

RUN crontab -l | { cat; echo "12	00	*	*	*	cd /app && python3 main.py"; } | crontab -

#CMD ["/bin/ash"]
CMD ["crond", "-f"]