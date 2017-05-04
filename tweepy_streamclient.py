# -*- coding: utf-8 -*-
from tweepy import StreamListener, API, Stream, OAuthHandler
from bson.json_util import loads
from dateutil.parser import parse # parsing tweet timestamps
import HTMLParser # parsing unicode text/symbols in py2.7
html_parser = HTMLParser.HTMLParser()
import re # curseword filtering
import pymongo # sending streamed tweets to mlab
import geojson # subsetting tweet payload content
import requests # sending geojson to mapbox, querying instagram api


# get some user-defined parameters
import settings

# customized class inheriting the tweepy.StreamListener
class BirdsEye_StreamListener(StreamListener):
    # print a message to console notifying a successful tweepy connection
    def on_connect(self):
        print "Connected to Twitter Streaming API."
        
    # on_status() is a bit nicer to use than on_data() because 
    # the status object is pre-processed by tweepy
    def on_status(self, status):
        # ignore retweets
        if not(status.retweeted):
            # get coordinates (preferable)
            if status.coordinates:
                # generate a mongdb id
                mongo_id = pymongo.database.ObjectId()
                # send the entire payload to mongodb
                send_to_mongodb(status, mongo_id)
                # send to mapbox
                send_to_mapbox(status, mongo_id)
                
                print(u"\n{} | {} | {}".format(status.created_at, status.author.screen_name, html_parser.unescape(status.text.replace("\n", " "))))
                print(u"coords: {}".format(status.coordinates))
                
                # first check for presence of extended attributes
                if u"extended_entities" in status.__dict__:
                    for xtmedia_item in status.extended_entities['media']:
                        # check first for photo
                        if xtmedia_item['type'] == u'photo':
                            print(u"xtmedia(photo): {}".format(xtmedia_item['media_url']))
                        # check for animated gif
                        elif xtmedia_item['type'] == u'animated_gif':
                            gif_variants = xtmedia_item['video_info']['variants']
                            for gif in gif_variants:
                                print(u"xtmedia(gif): {}".format(gif['url']))
                        # check for video
                        elif xtmedia_item['type'] == u'video':
                            video_variants = xtmedia_item['video_info']['variants']
                            for video in video_variants:
                                print(u"xtmedia(video): {}".format(video['url']))
                    
                # second check for non-extended media
                elif u'media' in status.entities:
                    for media_item in status.entities['media']:
                        # check based on keyword in media['expanded_url']
                        if media_item['expanded_url'].split("/")[-2] == u'photo':
                            print(u"media(photo): {}".format(media_item['media_url']))
                        # this might be obsolete with the new extended_entities check
                        elif media_item['expanded_url'].split("/")[-2] == u'video':
                            print(u"media(video): {}".format(media_item['expanded_url']))
                    
                # final check for 3rd-party urls
                if len(status.entities['urls']) <> 0:
                    for url_item in status.entities['urls']:
                        print(u"urls: {}".format(url_item['expanded_url']))
                    
                        
            # ...or place     
            elif status.place:
                print(u"\n{} | {} | {}".format(status.created_at, status.author.screen_name, html_parser.unescape(status.text.replace("\n", " "))))
                print(u"place: {}, {}".format(status.place.full_name, status.place.country_code))
                
                # first check for presence of extended attributes
                if u"extended_entities" in status.__dict__:
                    for xtmedia_item in status.extended_entities['media']:
                        # check first for photo
                        if xtmedia_item['type'] == u'photo':
                            print(u"xtmedia(photo): {}".format(xtmedia_item['media_url']))
                        # check for animated gif
                        elif xtmedia_item['type'] == u'animated_gif':
                            gif_variants = xtmedia_item['video_info']['variants']
                            for gif in gif_variants:
                                print(u"xtmedia(gif): {}".format(gif['url']))
                        # check for video
                        elif xtmedia_item['type'] == u'video':
                            video_variants = xtmedia_item['video_info']['variants']
                            for video in video_variants:
                                print(u"xtmedia(video): {}".format(video['url']))
                    
                # second check for non-extended media
                elif u'media' in status.entities:
                    for media_item in status.entities['media']:
                        # check based on keyword in media['expanded_url']
                        if media_item['expanded_url'].split("/")[-2] == u'photo':
                            print(u"media(photo): {}".format(media_item['media_url']))
                        # this might be obsolete with the new extended_entities check
                        elif media_item['expanded_url'].split("/")[-2] == u'video':
                            print(u"media(video): {}".format(media_item['expanded_url']))
                    
                # final check for 3rd-party urls
                if len(status.entities['urls']) <> 0:
                    for url_item in status.entities['urls']:
                        print(u"urls: {}".format(url_item['expanded_url']))
            
    # handling HTTP:420 / HTTP:429 errors (unofficial twitter rate limiting errors)
    def on_error(self, status_code):
        if status_code in [420, 429]:
            print(u"***RATE LIMITED")
            return False # disconnects the stream

# the tweet streamer that ingests incoming payloads            
def stream_tweets(c_k, c_s, a_t, a_s):
    # setup Twitter OAuth with input credentials
    auth = OAuthHandler(c_k, c_s)
    auth.set_access_token(a_t, a_s)
    # create the tweepy API and customized StreamListener
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    currStreamListener = BirdsEye_StreamListener()
    # endless loop that hopefully catches any errors and restarts the stream
    #   IncompleteReadError: Program falls too far behind incoming tweet volume
    while True:
        try:
            myStream = Stream(auth=api.auth, listener=currStreamListener)
            # filter for terms and languages based on settings.py config values
            myStream.filter(track=settings.filter_terms, languages=settings.filter_lang)
        except Exception as e:
            print e.message
            pass

        
# http://stackoverflow.com/a/6117124
# WIP
def curse_filter(payload_text):
    rep_list = {u"curseword":u"specialchars"}
    rep_list = dict((re.escape(k), v) for k, v in rep_list.iteritems())
    pattern = re.compile("|".join(rep_list.keys()))
    return pattern.sub(lambda m: rep_list[re.escape(m.group(0))], payload_text)

    
# here is where a tweet will be sent to the database for further QC
def send_to_mongodb(tweet_status, mdb_id):
    # first dump the tweepy Status object from json -> string -> bson/json dictionary
    # kind of messy but avoids errors with tweet attribute parsing
    tweet_payload = loads(geojson.dumps(tweet_status._json))
    # update dictionary with the new ID
    tweet_payload['_id'] = mdb_id
    # connect to mongodb instance
    try:
        connection = pymongo.MongoClient(host=settings.mongo_host, port=settings.mongo_port)
        dev_collection = connection[settings.mongo_db]['dev']
    except pymongo.errors.ConnectionFailure:
        print "{} database unreachable".format(settings.mongo_db)
    # send the tweet to the database
    try:
        dev_collection.insert_one(tweet_payload)
    except pymongo.errors.WriteError:
        print "Database {} disk quota exceeded".format(settings.mongo_db)
    except pymongo.errors.InvalidBSON:
        print "BSON ObjectId invalid"
    except pymongo.errors.InvalidDocument:
        print "MongoDB document not formatted properly"

# if a tweet has lat/lon coordinates, we add to a MapBox dataset
# a lot of this is a repeat of what we do in on_status so it should be refactored
# TODO: support multi-item media lists
def send_to_mapbox(tweet_status, feature_id):
    # first dump the tweepy Status object from json -> string -> bson/json dictionary
    # kind of messy but avoids errors with tweet attribute parsing
    tweet_payload = loads(geojson.dumps(tweet_status._json))
    feature_properties = dict(lang = tweet_payload['lang'],
                              twitter_handle = ur"@{}".format(tweet_payload['user']['screen_name']),
                              time = parse(tweet_payload['created_at']).isoformat(),
                              mongodb_id = str(feature_id))
    
    payload_text = html_parser.unescape(tweet_payload['text'].replace("\n", " "))
    # remove tweet links in the text if they exist
    if len(tweet_payload['entities']['urls']) > 0:
        for link in tweet_payload['entities']['urls']:
            tweet_link = ur"{}".format(link['url'])
            payload_text = payload_text.replace(tweet_link,"")
    feature_properties['tweet_text'] = payload_text
    
    # geo-info
    tweet_geom = tweet_payload['coordinates']
    if tweet_geom is None: # Redundant check
        tweet_geom = tweet_payload['place']['bounding_box']
    
    # visual media 
    media_url = None
    entities_list = tweet_payload['entities'].keys()
    # sometimes, media isn't a valid key (e.g. if the media url is from instagram rather than pic.twitter)
    if 'media' in entities_list:
        # only grab the first media url if there are multiple
        media_url = tweet_payload['entities']['media'][0]['media_url']
    else:
        media_urls = tweet_payload['entities']['urls']
        for item in media_urls:
            if "instagram" in item['expanded_url']:
                media_url = pull_instagram_pic_url(item['expanded_url'])
                break
    feature_properties['media_url'] = media_url
    
    # Populate the geojson feature (either a Point or Polygon)    
    mapbox_feature = geojson.Feature(str(feature_id), tweet_geom, feature_properties)
    
    # setup the HTTPS request url
    mapbox_url = 'https://api.mapbox.com/datasets/v1/{}/{}/features/{}?access_token={}'.format(settings.mapbox_user, settings.mapbox_dataset_id, feature_id, settings.mapbox_dataset_token)
    
    # send the HTTP-PUT request
    r = requests.put(mapbox_url, json=mapbox_feature)
    if not r.status_code == 200:
        print "Failed to add mbox dataset feature {} -> HTTP-{} {}".format(feature_id, r.status_code, r.reason)

# retrieve the thumbnail url for an instagram link
def pull_instagram_pic_url(insta_url):
    r = requests.get('https://api.instagram.com/oembed?url={}'.format(insta_url))
    if not r.status_code == 200:
        print "Failed to pull instagram embed url. HTTP-{} {}".format(r.status_code, r.reason)
        return None
    return r.json()['thumbnail_url']


if __name__ == "__main__":
    try:
        stream_tweets(settings.twitter_consumer_key, settings.twitter_consumer_secret, settings.twitter_access_token, settings.twitter_access_secret)
    except:
        print "Error initializing, check your settings.py and other.py"
        exit(1)
