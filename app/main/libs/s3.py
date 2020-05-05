import os
import boto3


class S3:
    S3_ACCESS_KEY = os.environ.get("S3_KEY")
    S3_SECRET_KEY = os.environ.get("S3_SECRET")

    @classmethod
    def get_client(cls):
        return boto3.client(
            's3',
            aws_access_key_id=cls.S3_ACCESS_KEY,
            aws_secret_access_key=cls.S3_SECRET_KEY
        )