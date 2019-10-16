# uptime-percentage-calculator
* Calculates your web service uptime based on Cloudwatch metrics of Route 53 healthcheck, and posts it to slack
* Made with Serverless Framework

## Prerequisite
* Configure Route 53 healthcheck resource to check your website
* Install Serverless Framework
  * ref. [Serverless Getting Started Guide](https://serverless.com/framework/docs/getting-started/)
* Set Slack webhook url and more to SSM Parameter Store, if you want to encrypt them

## Update serverless.yml
* Required parameter
  * HookUrl: Slack Webhook URL (like `https://hooks.slack.com/services/xxx/xxx/xxx`)
  * slackChannel: Channel to post uptime percentage
  * HealthcheckId: ID of Route 53 healthcheck

## Deploy

In order to deploy the endpoint you simply run

```bash
serverless deploy
```

The expected result should be similar to:

```bash
Serverless: Packaging service...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading service .zip file to S3 (1.47 KB)...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
..............
Serverless: Stack update finished...

Service Information
service: scheduled-cron-example
stage: production
region: us-east-1
api keys:
  None
endpoints:
  None
functions:
  cron: uptime-percentage-calculator-production-cron
```

There is no additional step required. Your defined schedule becomes active right away after deployment.

## Usage

To see your cron job running tail your logs with:

```bash
serverless logs --function cron --tail
```

The expected result should be similar to:

```bash
START RequestId: eddf3fbe0a-11e6-8d73bdd3836e44 Version: $LATEST
Invalid date	2009T12:28:03.214Z	eddf3fbe0a-11e6-8d73bdd3836e44	Your cron function uptime-percentage-calculator-production-cron ran at 12:28:03.214844
END RequestId: eddf3fbe0a-11e6-8d73bdd3836e44
REPORT RequestId: eddf3fbe0a-11e6-8d73bdd3836e44	Duration: 0.40 ms	Billed Duration: 100 ms 	Memory Size: 1024 MB	Max Memory Used: 16 MB
```
