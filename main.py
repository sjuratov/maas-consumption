import urllib.request
import json
import os
import ssl
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

endpoint = os.environ["endpoint"]
api_key = os.environ["api_key"]

if not api_key or not endpoint:
    raise Exception("A key and endpoint must be provided for inferencing")

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

# this line is needed if you use self-signed certificate in your scoring service.
allowSelfSignedHttps(True)

def get_data():
    import pandas as pd

    test_df = pd.read_json("./data/test_gen.jsonl", lines=True)
    test_df = test_df.sample(n=1)
    test_df.reset_index(drop=True, inplace=True)

    # sample request format - https://learn.microsoft.com/en-us/azure/ai-studio/reference/reference-model-inference-chat-completions#sample-request
    test_json = {
        "messages": test_df["messages"][0],
        "max_tokens": 500,
        "temperature": 0
        }    

    return test_json

get_req_body = get_data()
body = json.dumps(get_req_body).encode('utf-8')

# check API routes for the endpoint
url = f'{endpoint}/v1/chat/completions'
headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

req = urllib.request.Request(url=url, data=body, headers=headers)

try:
    response = urllib.request.urlopen(req)
    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))