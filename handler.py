import boto3
import datetime
import json
import logging
import os

from base64 import b64decode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

SLACK_CHANNEL = os.environ['slackChannel']
HOOK_URL = os.environ['HookUrl']
HEALTHCHECK_ID = os.environ['HealthcheckId']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_metrics_1day(date):
    starttime = date.replace(hour=0, minute=0, second=0, microsecond=000000)
    endtime = date.replace(hour=23, minute=59, second=59, microsecond=999999)

    return boto3.client('cloudwatch', region_name='us-east-1').get_metric_statistics(
        Namespace='AWS/Route53',
        MetricName='HealthCheckPercentageHealthy',
        Dimensions=[
            {
                'Name': 'HealthCheckId',
                'Value': HEALTHCHECK_ID
            }
        ],
        StartTime=starttime,
        EndTime=endtime,
        Period=60,
        Statistics=[
            'Average'
        ]
    )


def extract_healthcheck_results_per_min(metrics):
    datapoints = map(lambda x: x['Datapoints'], metrics)
    healthcheck_results_per_day = map(
        lambda x: [d.get('Average') for d in x], datapoints)
    return sum(healthcheck_results_per_day, [])


def calculate_uptime_percentage(healthcheck_results):
    if not healthcheck_results:
        logger.error("Metrics not available yet.")
        return False

    uptimes = list(filter(lambda x: x > 66.6, healthcheck_results))
    return round(len(uptimes)/len(healthcheck_results), 5)*100


def run(event, context):
    startdate = (datetime.datetime.now() - datetime.timedelta(days=7))
    datelist = [startdate + datetime.timedelta(days=day) for day in range(7)]

    metrics = map(get_metrics_1day, datelist)
    healthcheck_results = extract_healthcheck_results_per_min(metrics)
    uptime_percentage = calculate_uptime_percentage(healthcheck_results)

    if uptime_percentage is False:
        return "Abnormal end."

    message = '''
    * * Uptime percentage of last week ({startdate} ~ {enddate})*
    {uptime_percentage} %
    '''.format(
        uptime_percentage=uptime_percentage,
        startdate=datelist[0].strftime("%Y/%m/%d"),
        enddate=datelist[-1].strftime("%Y/%m/%d")
    ).strip()

    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': message
    }

    req = Request(HOOK_URL, json.dumps(slack_message).encode('utf-8'))
    try:
        response = urlopen(req)
        response.read()
        logger.info("Message posted to %s", slack_message['channel'])
    except HTTPError as e:
        logger.error("Request failed: %d %s", e.code, e.reason)
    except URLError as e:
        logger.error("Server connection failed: %s", e.reason)
