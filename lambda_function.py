import json
import urllib3
import hmac
import hashlib

MIST_WEBHOOK_SECRET='ReplaceMe'
DATADOG_ENDPOINT='https://http-intake.logs.ap1.datadoghq.com/api/v2/logs'
DATADOG_APIKEY='replacemer3p1ac3m3replacemer3p1a'

def do_auth(input_signature, body):
  secret = str.encode(MIST_WEBHOOK_SECRET)
  encoded_body = str.encode(body)
  expected_sig = hmac.new(secret, encoded_body, hashlib.sha256).hexdigest()
  if input_signature != expected_sig:
    print("Unexpected signature! Wrong secret?")
    return False
  return True

def lambda_handler(event, context):
  try:
    # Authenticate
    if MIST_WEBHOOK_SECRET != '':
      sig = event.get('headers', {}).get('x-mist-signature-v2', 'null')
      if not do_auth(sig, event['body']):
        return {
            'statusCode': 401,
            'body': ''
        }

    # Process Events
    input_json = json.loads(event['body'])
    payload = []
    for ev in input_json['events']:
      ev['topic'] = input_json['topic']

      # generate tags for datadog
      tags = f"topic:{input_json['topic']}"
      if 'site_name' in ev:
        tags += f",site:{ev['site_name']}"

      # convert event data to simple string
      pairs = []
      for k, v in ev.items():
        if isinstance(v, (list, tuple, dict)):
          continue
        elif isinstance(v, str):
          pairs.append(f'{k}="{v}"')
        else:
          pairs.append(f'{k}={v}')
      msg = " ".join(pairs)

      # generate log entry for datadog to ingest
      out = {
          'ddsource': 'mist',
          "ddtags": tags,
          'hostname': 'mist',
          'message': msg,
          'service': 'mist'
      }
      payload.append(out)
   
    # Send to Datadog
    headers = {
        'Content-Type': 'application/json',
        'DD-API-KEY': DATADOG_APIKEY
    }
    http = urllib3.PoolManager()
    response = http.request('POST', DATADOG_ENDPOINT, body=json.dumps(payload), headers=headers)
         
    return {
          'statusCode': response.status,
          'body': response.data.decode('utf-8')
    }
  except Exception as e:
    print(f"Exception has occurred! {e}")
    return {
        'statusCode': 500,
        'body': str(e)
    }

