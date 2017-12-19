# Exif data visualisation

A Python3 script using [exiftool](https://sno.phy.queensu.ca/~phil/exiftool/), 
[plotly](https://plot.ly/python/) and [mongodb](https://www.mongodb.com/) to visualise 
the exif meta data contained in your photographs.

## Setup
Run `brew install exiftool` and `pip3 install -r requirements.txt`.

We also need a running mongodb instance to store the extracted meta data. 

You can use docker to run a mongodb database.

```
$ docker run -p 27017:27017 --name metadata-mongo -d mongo
```

## Creating the Charts
Run the script with the absolute path to the directory containing your images.
```
$ ./visualise_meta_data.py /Users/ked/Photography/Images
```
