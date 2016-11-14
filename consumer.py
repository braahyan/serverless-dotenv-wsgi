import boto3
import settings
import os


def handler(event, context):
    queue_name = os.environ.get("TABLE_NAME")
    sqs = boto3.resource('sqs')
    print queue_name
    # Get the queue. This returns an SQS.Queue instance
    queue = sqs.get_queue_by_name(QueueName=queue_name)
    messages = queue.receive_messages(
        MaxNumberOfMessages=10, WaitTimeSeconds=5)
    for message in messages:
        # Let the queue know that the message is processed
        print message.body
        message.delete()
