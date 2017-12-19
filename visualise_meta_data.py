#!/usr/bin/env python3

import sys
import subprocess
import os
import json
from datetime import datetime, date

from pymongo import MongoClient

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Pie, Figure, Layout, Heatmap, Scatter


def import_meta_data(directory):
    def all_images(directory):
        for dirpath, _, filenames in os.walk(directory):
            for f in filenames:
                if not f.startswith("."):
                    yield os.path.abspath(os.path.join(dirpath, f))

    def export_meta_data(image, output_format='-json'):
        metadata = subprocess.check_output(['exiftool', output_format, image]).decode('utf-8')
        if output_format == '-json':
            return next(iter(json.loads(metadata)))
        return metadata

    client = MongoClient('localhost', 27017)
    exif = client.metadata.exif
    for image in all_images(directory):
        meta_data = export_meta_data(image)
        exif.insert_one(meta_data)
        print('.', end='', flush=True)


def focal_lengths_pie_chart():
    def gather_data():
        client = MongoClient('localhost', 27017)
        exif = client.metadata.exif
        
        map = """
        function focalLengthMap() {
            if (this.FocalLength == null || this.FocalLength == 'undef') return;
            emit(this.FocalLength, 1);
        }"""

        reduce = """
        function focalLengthReduce(key, values) {
            return Array.sum(values);
        }"""
        
        return exif.map_reduce(map, reduce, "focal_lenght_results").find()

    def create_pie_chart(results):
        labels = []
        values = []
        for result in results:
            labels.append(result['_id'])
            values.append(result['value'])
        plot([Pie(labels=labels, values=values)], filename='%s_focal_lengths.html' % date.today().strftime('%Y-%m-%d'))
    
    create_pie_chart(gather_data())


def time_of_day_heatmap():
    def gather_data():
        client = MongoClient('localhost', 27017)
        exif = client.metadata.exif

        events = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Monday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Tuesday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Wednesday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Thursday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Friday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], # Saturday
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  # Sunday
        ]

        for result in exif.find():
            if result['CreateDate'] is not None:
                parsed_date = datetime.strptime(result['CreateDate'], '%Y:%m:%d %H:%M:%S')
                hour = parsed_date.hour
                weekday = parsed_date.weekday()
                events[weekday][hour] += 1
        return events

    def create_heatmap(events):
        hours = ['00','01','02','03','04','05','06','07','08','09','10', '11','12','13','14','15','16','17','18','19','20','21','22','23']
        days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday', 'Sunday']
        heatmap = Heatmap(z=events, y=days, x=hours, colorscale='Viridis')
        layout = Layout(title='Pictures per weekday &amp; time of day', xaxis={'tickmode': 'linear'})
        plot(Figure(data=[heatmap], layout=layout), filename='%s_pictures_per_weekday_and_time_of_day.html' % date.today().strftime('%Y-%m-%d'))

    create_heatmap(gather_data())


def aperture_and_shutter_speed_bubble_chart():
    def gather_data():
        client = MongoClient('localhost', 27017)
        exif = client.metadata.exif
        
        map = """
        function focalLengthMap() {
            if (!this.Aperture || this.Aperture === 'undef') return;
            if (!this.ShutterSpeed || this.ShutterSpeed === 'undef') return;
            emit({aperture: this.Aperture, shutterSpeed: this.ShutterSpeed}, 1);
        }"""

        reduce = """
        function focalLengthReduce(key, values) {
            return Array.sum(values);
        }"""
        
        return exif.map_reduce(map, reduce, "aperture_and_shutter_speeds").find()
    
    def create_bubble_chart(events):
        shutter_speed = []
        aperture = []
        size = []
        text = []

        for event in events:
            aperture.append(event['_id']['aperture'])
            shutter_speed.append(event['_id']['shutterSpeed'])
            size.append(event['value'])
            text.append('Aperture: %s<br>Shutter Speed: %s<br>Size: %s' % (event['_id']['aperture'], event['_id']['shutterSpeed'], event['value']))

        trace = Scatter(
            x=shutter_speed, 
            y=aperture, 
            mode='markers',
            marker={
                'size': size
            },
            text=text
        )

        layout= Layout(
            title='Aperture and Shutter Speeds', 
            hovermode='closest',
            xaxis={
                'title': 'Shutter Speed',
                'ticklen': 5,
                'zeroline': False,
                'gridwidth': 2
            },
            yaxis={
                'range': [0, 25],
                'title': 'Aperture',
                'ticklen': 5,
                'gridwidth': 2,
                'zeroline': False
            },
            showlegend=False
        )

        plot(Figure(data=[trace], layout=layout), filename='%s_aperture_and_shutter_speed.html' % date.today().strftime('%Y-%m-%d'))

    create_bubble_chart(gather_data())


if __name__ == "__main__":
    import_meta_data(next(iter(sys.argv[1:])))

    focal_lengths_pie_chart()
    time_of_day_heatmap()
    aperture_and_shutter_speed_bubble_chart()
