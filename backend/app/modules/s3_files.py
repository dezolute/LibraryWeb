# import boto3
# import uuid
#
# from app.config import s3_config
#
#
# def get_s3_client():
#     client = boto3.client('s3',
#         endpoint_url='http://localhost:9000',
#         aws_access_key_id="minioadmin",
#         aws_secret_access_key="minioadmin",
#     )
#
#     return client
#
# def s3_create_bucket(bucket_name):
#     s3_client = get_s3_client()
#
#     response = s3_client.list_buckets()
#     existing_buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
#
#     if not bucket_name in existing_buckets:
#         s3_client.create_bucket(Bucket=bucket_name)
#
#
# def upload_file_to_s3(file):
#     s3 = get_s3_client()
#     s3_create_bucket(s3_config.BUCKET_NAME)
#
#     s3.upload_file(
#         Filename=file,
#         Bucket=s3_config.BUCKET_NAME,
#         Key=f"{uuid.uuid4()}.{file.split('.')[-1]}",
#     )
#
#