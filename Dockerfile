FROM python:3

ADD gpx.py /
ADD strava_local_heatmap.py /
ADD requirements.txt /


RUN mkdir gpx
RUN pip install -r requirements.txt

CMD [ "python", "gpx.py" ]