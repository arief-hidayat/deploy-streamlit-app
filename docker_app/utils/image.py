import io
import re
import boto3


class ImageRenderer:

    def __init__(self, region):
        self.s3_client = boto3.Session(region_name=region).client('s3')

    # Get S3 file contents
    def get_file_from_s3(self, s3_path):
        bucket_object_pattern = r"s3://([^/]+)/(.+)"
        match = re.match(bucket_object_pattern, s3_path)

        bucket_name, object_key = match.groups()

        response = self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response["Body"].read()
        return file_content

    def render_s3_image(self, agent_response, st):
        s3_path_pattern = r"s3://[^\s<.\"]+"
        s3_paths = re.findall(s3_path_pattern, agent_response)
        if s3_paths:
            file_content = self.get_file_from_s3(s3_paths[0])
            st.image(io.BytesIO(file_content), caption="Image from S3", width=256)

    @staticmethod
    def get_s3_url_from_ref(ref):
        file = ref.split('/')[-1]
        s3_bucket = ref.split('//')[1].split('/')[0]
        s3_url = f'https://us-east-1.console.aws.amazon.com/s3/object/{s3_bucket}?region=us-east-1&bucketType=general&prefix={file}'
        s3_url = s3_url.replace(' ', '')
        return s3_url
