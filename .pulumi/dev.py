"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3

def deploy(stage):

    # Create an AWS resource (S3 Bucket)
    bucket = s3.BucketV2('my-bucket')

    # Export the name of the bucket
    pulumi.export('bucket_name', bucket.id)

    print(bucket.id)
