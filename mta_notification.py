from google.transit import gtfs_realtime_pb2
import requests
import time # imports module for Epoch/GMT time conversion
import os # imports package for dotenv
from dotenv import load_dotenv, find_dotenv # imports module for dotenv
from protobuf_to_dict import protobuf_to_dict
load_dotenv(find_dotenv()) # loads .env from root directory



# See MTA Google Group post for discussion on this authentication header; you get 403 errors without it:
# https://groups.google.com/g/mtadeveloperresources/c/t8anoGP5S8U/m/Ke3lxu-1CAAJ
class TokenAuth(requests.auth.AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['x-api-key'] = f'{self.token}'  # Python 3.6+
        return r


# The root directory requires a .env file with API_KEY assigned/defined within
# and dotenv installed from pypi. Get API key from http://datamine.mta.info/user
api_key = os.environ['API_KEY']

# returns the URL for specific train feed based on user input
def get_train_url(train):
    if train=='L':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l'
    elif train=='G':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g'
    elif train=='B' or train=='D' or train=='F' or train=='M':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm'
    elif train=='1' or train=='2' or train=='3' or train=='4' or train=='5' or train=='6' or train=='7':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs'
    elif train=='N' or train=='Q' or train=='R' or train=='W':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw'
    elif train=='A' or train=='C' or train=='E':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace'
    elif train=='J' or train=='Z':
        return 'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz'
    else:
        return "invalid"
    



# Requests subway status data feed from City of New York MTA API
def get_feed(train_url):
    feed = gtfs_realtime_pb2.FeedMessage()
    response = ''
    while response == '':
        try:
            response = requests.get(url=train_url, auth=TokenAuth(api_key))
        except requests.exceptions.ConnectionError:
            print("Connection refused...trying again")
            time.sleep(5)
            continue
    feed.ParseFromString(response.content)
    subway_feed = protobuf_to_dict(feed) # subway_feed is a dictionary
    print(subway_feed)
    # TODO - Code will KeyError on the below line if no trains are scheduled (ie: entire line is suspended)
    # TODO - This happens frequently with the G on nights and weekends, but I imagine it never came up on the BDFM
    realtime_data = subway_feed['entity'] # train_data is a list
    return realtime_data

# The MTA data feed uses the General Transit Feed Specification (GTFS) which
# is based upon Google's "protocol buffer" data format. While possible to
# manipulate this data natively in python, it is far easier to use the
# "pip install --upgrade gtfs-realtime-bindings" library which can be found on pypi


# This function takes a converted MTA data feed and a specific station ID and
# loops through various nested dictionaries and lists to (1) filter out active
# trains, (2) search for the given station ID, and (3) append the arrival time
# of any instance of the station ID to the collected_times list
def station_time_lookup(train_data, station):
    collected_times = []
    for trains in train_data: # trains are dictionaries
        if trains.get('trip_update', False) != False:
            unique_train_schedule = trains['trip_update'] # train_schedule is a dictionary with trip and stop_time_update
            #print(unique_train_schedule['stop_time_update'])
            try:
                unique_arrival_times = unique_train_schedule['stop_time_update'] # arrival_times is a list of arrivals
            except KeyError:
                print('KeyError exception caught!')
                return ['9999']
            for scheduled_arrivals in unique_arrival_times: #arrivals are dictionaries with time data and stop_ids
                if scheduled_arrivals.get('stop_id', False) == station:
                    time_data = scheduled_arrivals['arrival']
                    unique_time = time_data['time']
                    if unique_time != None:
                        collected_times.append(unique_time)
    #print(collected_times)
    return collected_times

# Pop off the earliest and second earliest arrival times from the list minus times that
# you can't get to in time set by cutoff_min variable
def get_next_times(collected_times, cutoff_min):
    collected_times.sort()
    nearest_arrival_time = collected_times[0]
    #second_arrival_time = collected_times[1]
    print(collected_times)

    # Grab the current time so that you can find out the minutes to arrival
    current_time = int(time.time())
    if nearest_arrival_time == '9999':
        return 'NR', 'NR'
    else:
        time_until_train = int(((nearest_arrival_time - current_time) / 60))
        k=1
        while time_until_train < cutoff_min:
            time_until_train = int(((collected_times[k] - current_time) / 60))
            k+=1
        second_train = int(((collected_times[k] - current_time) / 60))
        return time_until_train, second_train


# EXAMPLE USAGE
# station1N = "L10N"
# WALK_TIME = 6
# rtd1 = mta_notification.get_feed(train1url)
# times1N = mta_notification.station_time_lookup(rtd1,station1N)
# next1N, next1N2 = mta_notification.get_next_times(times1N,WALK_TIME)


# These are useful print statments used for script debugging, commented out
#
# for times in collected_times:
#     print(times, "=", time.strftime("%I:%M %p", time.localtime(times)))
# print(collected_times)
# print(nearest_arrival_time)
# print(second_arrival_time)
# print(time_until_train)