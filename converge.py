#!/usr/bin/env python

import boto3
from botocore.exceptions import ClientError
import sys
import yaml
import datetime

def main():
    with open(sys.argv[1], 'r') as f:
        items = yaml.load(f)
#        print items
        client = boto3.client('swf')
        try:
            response = client.list_open_workflow_executions(
                domain = 'loops',
                startTimeFilter = {
                    'oldestDate': datetime.datetime(1970, 1, 1),
                },
            )
            del response['ResponseMetadata']
            if response:
                flows = [flow['execution']['workflowId'] for flow in response['executionInfos'] if flow['cancelRequested'] == False]
                adds = [i for i in items if i not in flows]
                dels = [f for f in flows if f not in items]
                for a in adds:
                    print "Starting %s" % a
                    client.start_workflow_execution(
                        domain = 'loops',
                        workflowId = a,
                        workflowType = {'name': 'workflow', 'version': '1.4'},
                        taskList = {'name': 'workflow'},
                        executionStartToCloseTimeout = '604800',
                        taskStartToCloseTimeout = 'NONE',
                        childPolicy = 'ABANDON',
                    )
                for d in dels:
                    print "Stopping %s" % d
                    client.request_cancel_workflow_execution(
                        domain = 'loops',
                        workflowId = d,
                    )
        except ClientError as e:
            raise

if __name__ == "__main__":
    main()


