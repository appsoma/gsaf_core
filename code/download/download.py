import sys
import time
import os
import re
import urlparse
import datetime
import json
import urllib2
import shutil


with open( "params.json" ) as f:
    params = json.loads( f.read() )

url = params['url']
parsed = urlparse.urlparse( url )

# FETCH the HTML file from S3 that contains the list of files to download
try:
	indexHTML = urllib2.urlopen(url).read()
except Exception, e:
	print "Unable to connect to index url,", e
	sys.exit(1)

m = re.search(r"for job (JA\d+), sequencing run (SA\d+)", indexHTML)
if m:
    job = m.group(1)
    seq = m.group(2)
else:
	print "Job number not found in HTML index"
	sys.exit(1)

# There is machine parseable JSON metadata in this file that tells us what needs to be downloads
files_to_download = []
url_to_index = {}
req_space_in_bytes = 0
output_folder = "./datasets/"+job+"-"+seq+"/"

try:
    os.mkdir( output_folder )
except:
    pass

found_json = False
for json_block in re.findall(r"\<\!\-\-\s*gsafjson(.*)\-\-\>", indexHTML):
	try:
		obj = json.loads(json_block)
	except:
		print "Invalid JSON block found in the source index file"
		print "Please contact Scott Hunicke Smith <scotth@austin.utexas.edu>"
		sys.exit(1)
	
	found_json = True

	url_to_index[ obj['url'] ] = len( files_to_download )

	req_space_in_bytes += float(obj['size_in_mb']) * 1024 * 1024
	files_to_download.append( obj )

if not found_json:
	print "There was no metadata in this html index."
	print "Possibly it is an old file and you may need a new key."
	print "Please contact Scott Hunicke Smith <scotth@austin.utexas.edu>"
	sys.exit(1)
	
# CHECK available disk space and setup info block
s = os.statvfs( output_folder )
avail_in_bytes = s.f_bavail * s.f_frsize
if req_space_in_bytes > avail_in_bytes:
	print "You do not have enough space to download all of the files. Exiting."
	sys.exit(1)

# DOWNLOAD the individual files
idx = 0
for i in files_to_download:
    idx += 1
    print "Downloading", idx, "of", len(files_to_download)
    path = os.path.join( output_folder, i['filename'] )
    parsed = urlparse.urlparse( i['url'] )
	# Mysteriously the parsed geturl makes this work.  I think it has something
	# do to with the unescaped characters in the path but I can't see that
	# urlparse.geturl actually fixes it.
    try:
        req = urllib2.urlopen( parsed.geturl() )
        with open( path, 'wb' ) as fp:
            shutil.copyfileobj( req, fp )

    except Exception, e:
        print "Unable to load file. Perhaps the keys are old.", e
        sys.exit(0)
