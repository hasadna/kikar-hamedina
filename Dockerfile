FROM python:2
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
ADD requirements/ /app/requirements/
RUN pip install -r /app/requirements/vps.txt
ADD kikar_hamedina /app/
EXPOSE 8000
COPY start.sh /usr/bin

RUN useradd -s /bin/bash -u 3000 -m kikar_user
RUN chown kikar_user /usr/bin/start.sh
RUN chown -R kikar_user /app
RUN chown -R kikar_user /home/kikar_user

USER kikar_user
CMD ["/bin/bash", "/usr/bin/start.sh"]
