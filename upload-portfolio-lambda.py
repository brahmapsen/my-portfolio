import boto3
from botocore.client import Config

import StringIO
import zipfile
import mimetypes

def handler (event, context):
    sns=boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:293577862734:deployPortfolioTopic')

    try:
        s3=boto3.resource('s3',config=Config(signature_version='s3v4'))

        portfolio_bucket = s3.Bucket('portfolio.inagetech.com')
        build_bucket = s3.Bucket('portfoliobuild.inagetech.com')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip',portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio deployed", Message="Portfolio deployed successfully.")

    except:
        topic.publish(Subject="Portfolio deploy failed", Message="The portfolio deploy failed..")
        raise
    return 'Job done'
