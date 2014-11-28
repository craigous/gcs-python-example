#
# GCS JSON API example from https://developers.google.com/storage/docs/json_api/v1/json-api-python-samples
#

import os
import sys
import json
import httplib2
import argparse

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

BUCKET_NAME = 'bucket-name'
API_VERSION = 'v1'
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
    'https://www.googleapis.com/auth/devstorage.full_control',
    'https://www.googleapis.com/auth/devstorage.read_only',
    'https://www.googleapis.com/auth/devstorage.read_write',
  ],
  message=tools.message_if_missing(CLIENT_SECRETS))

parser = argparse.ArgumentParser(
  description=__doc__,
  formatter_class=argparse.RawDescriptionHelpFormatter,
  parents=[tools.argparser])

def main(argv):
  flags = parser.parse_args(argv[1:])
  
  storage = file.Storage('oauth.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)
  
  http = httplib2.Http()
  http = credentials.authorize(http)
  
  service = discovery.build('storage', API_VERSION, http=http)
  
  try:
    req = service.buckets().get(bucket=BUCKET_NAME)
    resp = req.execute()
    print json.dumps(resp, indent=2)

    fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
    req = service.objects().list(bucket=BUCKET_NAME, fields=fields_to_return)
    # If you have too many items to list in one request, list_next() will
    # automatically handle paging with the pageToken.
    
    while req is not None:
      resp = req.execute()
      print json.dumps(resp, indent=2)
      req = service.objects().list_next(req, resp)

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")
  
if __name__ == "__main__":
  main(sys.argv)