"""
Quick script to upload existing markers to S3 using Bucketeer created creds
"""
import os
from os.path import join

from boto.s3.connection import S3Connection
from boto.s3.key import Key

aws_bucket_url = 'https://bucketeer-some-url.s3.amazonaws.com'
aws_access_key = 'aws-access'
aws_secret = 'aws-secret'
conn = S3Connection(aws_access_key, aws_secret)

bucket_name = 'ye-bucket-name'
bucket = conn.create_bucket(bucket_name)

def list_items():
    """list items in bucket"""
    for k in bucket.list():
        print k.name, k.size

def get_key_names():
    """get key names"""
    knames = []
    for k in bucket.list():
        knames.append(k.name)
    return knames

def add_markers(makers_only=True):
    """add markers"""

    marker_dir = '../media/uploads'
    fnames = os.listdir(marker_dir)


    if markers_only:
        # Only upload files ending in "_markers."
        fnames = [x for x in fnames if x.find('_markers.') > -1]

    current_keys = get_key_names()

    cnt = 0
    for marker_name in fnames:
        cnt+=1
        print '\n%s) %s' % (cnt, marker_name)

        key_name = 'logos/%s' % marker_name
        print '     key_name: %s' % key_name

        # have we already uploaded this?
        if key_name in current_keys:
            print 'already in S3'
            continue

        # grab file contents
        full_name = join(marker_dir, marker_name)
        fcontents = open(full_name, 'rb').read()

        # upload to S3
        k = Key(bucket)
        k.key = key_name
        k.set_contents_from_string(fcontents)
        print 'uploaded: %s' % key_name

        # allow public read of item
        bucket.set_acl('public-read', key_name)
        print 'allow public read: %s/%s' % (aws_bucket_url, key_name)

        if cnt==25:
            break

if __name__=='__main__':
    #list_items()
    add_markers()
