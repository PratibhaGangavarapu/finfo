import time
import random
import csv
import json
import os
import requests as rq
import logging
import argparse
import datetime
#from google.cloud import pubsub
from google.cloud import pubsub
from csv import reader
from google.cloud import storage
dir = os.getcwd()
bucket_name='gs://striped-impulse-352211/raw_pe_tdata.csv'
os.system('gsutil cp '+ bucket_name  +' '+ dir)
data_file = os.path.join(dir,'raw_pe_tdata.csv')

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TOPIC = 'priv-equity'
INPUT = 'raw_pe_tdata.csv'

def publish(publisher, topic, events):
   numobs = len(events)
   if numobs > 0:
      # logging.info('Publishing {0} events from {1}'.format(numobs, get_timestamp(events[0])))
       for event_data in events:
         ## convert from bytes to str
          event_data = event_data.encode('utf-8')

          publisher.publish(topic,event_data)

def get_timestamp(row):
     # look at first field of row
     timestamp = row["rec_crt_ts"]
     return datetime.datetime.strptime(timestamp,TIME_FORMAT)

def simulate(topic, ifp, firstObsTime, programStart):
       for line in ifp:
         topublish = list()
         event_data = json.dumps(line)
         to_sleep_secs = random.uniform(0.005,0.010)
         logging.info('Sleeping {} seconds'.format(to_sleep_secs))
         time.sleep(to_sleep_secs)
         topublish.append(event_data)
         publish(publisher, topic, topublish)
         
if __name__ == '__main__':
    #parser = argparse.ArgumentParser(description='Send sensor data to Cloud Pub/Sub in small groups, simulating real-time behavior')
    #parser.add_argument('--speedFactor', help='Example: 60 implies 1 hour of data sent to Cloud Pub/Sub in 1 minute', required=True, type=float)
    #parser.add_argument('--project', help='Example: --project $DEVSHELL_PROJECT_ID', required=True)
    #args = parser.parse_args()
    print("in main")
    # create Pub/Sub notification topic
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
publisher = pubsub.PublisherClient()
event_type = publisher.topic_path("striped-impulse-352211",TOPIC)
    # notify about each line in the input file
programStartTime = datetime.datetime.utcnow()
f_data = open(data_file)
fieldnames=("rec_crt_ts","company_name","growth_stage","country","state","city","continent","industry","sub_industry","client_focus",
            "business_model","company_status","round","amount_raised","currency","date","quarter","Month","Year","investor_types",
            "investor_name","company_valuation_usd","valuation_date")
n=0
reader = csv.DictReader(f_data, fieldnames)
next(reader)
for row in reader:
        if(n<1):
           firstObsTime = get_timestamp(row)
           logging.info('Sending finfo data from {}'.format(firstObsTime))
        else:
            break
        n=n+1
       
simulate(event_type, reader, firstObsTime, programStartTime)

