# Mist Webhook Events to Datadog Relay
This is a Python script which works on AWS Lambda to relay events from [Juniper Mist Cloud](https://www.juniper.net/us/en/products/mist-ai.html) to [Datadog](https://www.datadoghq.com/). 
![[img/screenshot.png]]

## Purpose
Juniper Mist sends network events over its Webhook API in its own JSON format. On the other hand, Datadog has [HTTP Log Intake API](https://docs.datadoghq.com/api/latest/logs/) which can receive logs over HTTP POST requests also in its own JSON format. Therefore, to ingest events from Mist to Datadog, we need an event relay which converts Mist's JSON format to Datadog's JSON format. This Python script provides this feature on AWS Lambda to receive Webhook API events from Mist, convert the JSON format, and send it to Datadog.

Below is an example event received over Webhook API from Mist:
```
{
  "topic": "client-join",
  "events": [
    {
      "ap": ???5c5b35d0xxxx",
      "ap_name": ???AP43 Test",
      "mac": "70ef0071xxxx",
      "site_id": "d761985e-49b1-4506-xxxx-xxxxxxxxxxx",
      "site_name": ???Tokyo",
      "ssid": ???Intranet-SSID",
      "timestamp": 1592333828,
      ...
    }
  ]
}
```

This Python script converts this event data to below JSON format which Datadog's HTTP Log Intake API can ingest:
```
[
  {
    "ddsource": "mist",
    "ddtags": "site:Tokyo,topic:client-join",
    "service": "mist",
    "message": "ap=\"5c5b35d0xxxx\" ap_name=\"AP43 Test\" mac=\"70ef0071xxxx\" site_id=\"d761985e-49b1-4506-xxxx-xxxxxxxxxxx\" site_name=\"Tokyo\" ssid=\"Intranet-SSID\" timestamp=1592333828 ..."
  }
]
```

## How to Use
First, on AWS console, create a Lambda function with the Python script in this repository, and generate a function URL to execute this Lambda function:
1. Create a AWS Lambda function
   Runtime should be configured as Python 3.x. Architecture can be any.
2. Copy lambda_function.py to the newly created Lambda function
3. Update the configuration variables (see below for explanation)
4. Generate Lambda function URL with no authentication (Auth type NONE)
   (Ex. https://xxx.lambda-url.ap-northeast-1.on.aws/)

Then, on Mist Cloud console, configure Webhook API to send events to the above Lambda function URL:
1. Open Organization settings or Site settings in Mist console
   (Webhook API can be configured per organization or per site)
2. Under Webhook API configuration pane, click "Add Webhook"
3. Select "HTTP POST" for Webhook Type
4. Enter the generated Lambda function URL in "URL"
5. For "Topics", select the events which you want to collect
6. Open Settings, and in "Secret", enter the authentication string which you have configured in the Python script (MIST_WEBHOOK_SECRET variable)
7. Click "Add"

## Configuration 
Below variable at the top of the script should be updated accordingly:
- MIST_WEBHOOK_SECRET: Any random string for authenticating data from Mist
- DATADOG_ENDPOINT: API endpoint for the HTTP Log Intake API
  (API endpoint is different per Datadog region)
- DATADOG_APIKEY: API key for Datadog

## Don't see logs?
It takes few minutes for Mist to start sending events over the Webhook API. You should wait for about 10 minutes for the event to appear.

If you still do not see the logs, you should check the AWS console to see if the Lambda function is called and there is no errors seen on the Lambda function logs. You can check the "Recent Invocations" under the Lambda monitor tab to see if the Lambda function is being called. You can also see logs for each execution by clicking on the LogStream button under each invocation entry.

## Reference
1. Mist Webhook API Documentation
   [https://www.juniper.net/documentation/us/en/software/mist/automation-integration/topics/topic-map/webhook-messages.html](https://www.juniper.net/documentation/us/en/software/mist/automation-integration/topics/topic-map/webhook-messages.html)
2. Datadog Log API Documentation
   [https://docs.datadoghq.com/api/latest/logs/](https://docs.datadoghq.com/api/latest/logs/)
