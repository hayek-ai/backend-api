import unittest

from main.libs.s3 import S3


class TestS3Lib(unittest.TestCase):
    @classmethod
    def test_get_client(cls):
        client = S3.get_client()
        assert str(type(client)) == "<class 'botocore.client.S3'>"
