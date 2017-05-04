# BirdsEye-Tweepy
Tracks mentions of ```settings.filter_terms``` in ```settings.filter_lang``` tweets, prints time/handle/text along with any included location info and/or media URLs to console while also sending location-enabled tweets to MongoDB and MapBox.

## Requirements
*The following assumes you have Anaconda ([http://continuum.io/downloads](http://continuum.io/downloads)) or Miniconda ([http://conda.pydata.org/miniconda.html](http://conda.pydata.org/miniconda.html)) installed and are familiar with their utilities*
```
conda create -n birdseye-tweepy python=2.7 pip pymongo requests dateutil -c defaults --override-channels
```
Following this command, you can switch to the newly created virtualenv using ```source activate birdseye-tweepy```(Linux/Unix) or ```activate birdseye-tweepy``` (Windows)

After this you will need to get Tweepy and GeoJSON via PyPI
```
pip install tweepy geojson
```

Once you have setup and activated your environment, create a file ```other.py``` in the same directory as ```tweepy_streamclient.py``` and populate it as follows (replacing parenthesized values with the actual credentials)

```
# Database connection info
mongo_host = (*mongo_host*) # URL to the mongodb instance
mongo_port = (*mongo_port*) # network port for the mongodb instance
mongo_db = (*mongo_db*) # name of the mongodb database

# Twitter Dev API keys
twitter_consumer_key = (*c_k*)
twitter_consumer_secret = (*c_s*)
twitter_access_token = (*a_t*)
twitter_access_secret = (*a_s*)

# MapBox API keys
mapbox_user = (*mapbox_user*)  # Username for MapBox API
mapbox_dataset_token = (*mapbox_dst*)  # MapBox Datasets API token
mapbox_dataset_id = (*ds_id*) # ID of the MapBox dataset that will receive geojson features
```

Assuming your target mongodb is available, you can now begin streaming tweets using the following:
```
python tweepy_streamclient.py
```

To change the filtered topics or languages, update the lists in ```settings.py```
