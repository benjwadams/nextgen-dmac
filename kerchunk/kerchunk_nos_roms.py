import fsspec
import ujson
from kerchunk.hdf import SingleHdf5ToZarr


def generate_kerchunked_ofs_aws(region: str, bucket: str, key: str, dest_bucket: str, dest_prefix: str):
     # For now SSL false is solving my cert issues **shrug**
    fs_read = fsspec.filesystem('s3', anon=True, skip_instance_cache=True, use_ssl=False)
    fs_write = fsspec.filesystem('s3', anon=False, skip_instance_cache=True, use_ssl=False)

    url = f"s3://{bucket}/{key}"
    filekey = key.split("/")[-1]
    outurl = f"s3://{dest_bucket}/{dest_prefix}/{filekey}.zarr"

    with fs_read.open(url) as ifile:
        print(f"Kerchunking nos model at {url}")
        chunks = SingleHdf5ToZarr(ifile, url)

        print(f"Writing kerchunked nos model to {outurl}")
        with fs_write.open(outurl, mode="w") as ofile:
            data = ujson.dumps(chunks.translate())
            ofile.write(data)
    
    print(f'Successfully processed {url}')


if __name__ == '__main__':
    import os
    sqs_message = {
        "Type": "Notification",
        "MessageId": "64e0cdc6-ce97-53cb-90b2-914f059429c1",
        "TopicArn": "arn:aws:sns:us-east-1:123901341784:NewOFSObject",
        "Subject": "Amazon S3 Notification",
        "Message": "{\"Records\":[{\"eventVersion\":\"2.1\",\"eventSource\":\"aws:s3\",\"awsRegion\":\"us-east-1\",\"eventTime\":\"2023-03-14T01:07:14.304Z\",\"eventName\":\"ObjectCreated:Put\",\"userIdentity\":{\"principalId\":\"AWS:AIDAJSLYAQIR3HHVYDOK2\"},\"requestParameters\":{\"sourceIPAddress\":\"34.195.147.78\"},\"responseElements\":{\"x-amz-request-id\":\"NS093145WJSB3M5P\",\"x-amz-id-2\":\"TBLTM5eN3RpYYyVJS0d1fGVwhpsjED4Tw7eZMf/D3sYJJNVpWg3TRw7X/pZ9S/mYIE8NWOZy8hDFgjGGMNzYTE2YZ+3S88dfwN32jnoeVrA=\"},\"s3\":{\"s3SchemaVersion\":\"1.0\",\"configurationId\":\"NTY5YmEwY2QtYzE3Zi00NTQ2LTllZTQtNzE1ZTEwMmIxMGFl\",\"bucket\":{\"name\":\"noaa-ofs-pds\",\"ownerIdentity\":{\"principalId\":\"A2AJV00K47QOI1\"},\"arn\":\"arn:aws:s3:::noaa-ofs-pds\"},\"object\":{\"key\":\"tbofs.20230314/nos.tbofs.fields.n002.20230314.t00z.nc\",\"size\":20138396,\"eTag\":\"6b6b182fdbacb0cfc7d491c0f48c7d26\",\"sequencer\":\"00640FC8C21FD07CDB\"}}}]}",
        "Timestamp": "2023-03-14T01:07:15.001Z",
        "SignatureVersion": "1",
        "Signature": "DsU2+uGwqEfGQ6EHSW/swtx6JqBplP5b0KXXSyPX4ewZMS29GaCtCGrowIsyW9nWAV3bI8tnD44/32wOU5Xvh1Xm2P1aocDuHkZAsSOi859OyaJcdyBIKT8txJbSo+X+ql6t/bO/pI/A0Cnjwn9pZDHul648UnQamL0jAyqWN+MWhGd8efO4dbrloq5Zi4wPI3KRWgE0L2aYg6IPXAHxm1S0u+996iL3MpxVrlGvLBdVFZXg14G53z83xAhlT2XmNzpcnHy9Pkl2a9LpXusesFNgyrsFmzq0cBXYAliSj0ALHxVSOpOK2sp4KL1UyKjy0HBwhUKv4pOdDTA02VQxmg==",
        "SigningCertURL": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem",
        "UnsubscribeURL": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:123901341784:NewOFSObject:d8f7dac5-0db1-4541-a0fb-4e13b43299f1"
    }

    message = ujson.loads(sqs_message["Message"])
    record = message["Records"][0]
    region = record["awsRegion"]
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    dest_bucket = 'nextgen-dmac'
    dest_prefix = 'nos'

    generate_kerchunked_ofs_aws(region, bucket, key, dest_bucket, dest_prefix)
