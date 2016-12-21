# BirdsEye-Tweepy
Tracks mentions of snow/neige in EN/FR tweets, prints time/handle/text along with any included location info and/or media URLs

## Requirements
*The following assumes you have Anaconda ([http://continuum.io/downloads](http://continuum.io/downloads)) or Miniconda ([http://conda.pydata.org/miniconda.html](http://conda.pydata.org/miniconda.html)) installed and are familiar with their utilities*
```
conda create -n birdseye-tweepy python=2.7 pip -c 'defaults' --override-channels --no-default-packages
```
Following this command, you can switch to the newly created virtualenv using ```source activate birdseye-tweepy```(Linux/Unix) or ```activate birdseye-tweepy``` (Windows)

After this you will need to get Tweepy via pip
```
pip install tweepy
```

Once you have setup your Twitter API key chain and are in the new virtualenv, running the script is as now as easy as 
```
python tweepy_streamclient.py <consumer key> <consumer secret> <access token> <access secret>
```
