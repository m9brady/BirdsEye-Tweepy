# -*- coding: utf-8 -*-
"""
Created on Fri Dec 09 11:56:01 2016
@author: Mikeb
"""
#import json
#print(json.dumps(<jsonobj>, indent=4)) #<-"pretty" printing of json
from tweepy import StreamListener, API, Stream, OAuthHandler
import HTMLParser # parsing unicode text/symbols in py2.7
html_parser = HTMLParser.HTMLParser()
import sys # argument passing
import re # curseword filtering


# customized class inheriting the tweepy.StreamListener
# TODO: decide whether to do main QA/QC here or send all viable tweets to DB and do checks later
class CPSStreamListener(StreamListener):
    # on_status() is a bit nicer to use than on_data() because 
    # the status object is pre-processed by tweepy
    def on_status(self, status):
        # ignore retweets
        if not(status.retweeted):
            # get coordinates (preferable) 
            if status.coordinates:
                print(u"\n{} | {} | {}".format(status.created_at, status.author.screen_name, html_parser.unescape(status.text.replace("\n", " "))))
                print(u"coords: {}".format(status.coordinates))
                
                # first check for presence of extended attributes
                if u"extended_entities" in status.__dict__:
                    # check first for photo
                    # TODO: support multi-photo media lists
                    for xtmedia_item in status.extended_entities['media']:
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
                    # check first for photo
                    # TODO: support multi-photo media lists
                    for xtmedia_item in status.extended_entities['media']:
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
                    
    # handling HTTP:420 errors (rate limiting)
    def on_error(self, status_code):
        if status_code == 420:
            print(u"***RATE LIMITED")
            return False # disconnects the stream

# the tweet streamer that ingests incoming payloads            
def stream_tweets(credentials):
    c_k, c_s, a_t, a_s = credentials
    # setup Twitter OAuth with input credentials
    auth = OAuthHandler(c_k, c_s)
    auth.set_access_token(a_t, a_s)
    # create the tweepy API and customized StreamListener
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    currStreamListener = CPSStreamListener()
    # endless loop that hopefully catches any errors and restarts the stream
    #   IncompleteReadError: Program falls too far behind incoming tweet volume
    while True:
        try:
            myStream = Stream(auth=api.auth, listener=currStreamListener)
            # Bilingual filter for snow in text payloads
            myStream.filter(track=['snow', 'neige'], languages=['en', 'fr'])
        except Exception as e:
            print e.message
            pass

        
# http://stackoverflow.com/a/6117124
def curse_filter(payload_text):
    rep_list = {u"curseword":u"specialchars"}
    rep_list = dict((re.escape(k), v) for k, v in rep_list.iteritems())
    pattern = re.compile("|".join(rep_list.keys()))
    return pattern.sub(lambda m: rep_list[re.escape(m.group(0))], payload_text)

    
# here is where a tweet will be sent to the database for further QC
def send_to_mongodb(tweet_payload):
    pass

    
def main(consumer_key=None, 
         consumer_secret=None,
         access_token=None,
         access_secret=None):
	if consumer_key and consumer_secret and access_token and access_secret:
		stream_tweets([consumer_key, consumer_secret, access_token, access_secret])
	else:
		print("Incorrect number of arguments passed. Exiting...")
		exit()

  
if __name__ == "__main__":
    # pass the necessary twitter API credentials in order of:
    # consumer key, consumer secret, access token, access secret
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
