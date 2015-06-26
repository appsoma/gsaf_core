import re
import sys
import json

sys.path.append("./code/welder_api")
import welder_api

print welder_api.expand_vars("test")
sys.exit(0)

with open( "params.json" ) as f:
    params = json.loads( f.read() )

pairs = {}
for file_path in params['fastq_files[]']:
	match = re.match( r'^(.*/)([^/]+)_R(\d)_([^/]+)$', file_path )
	if match:
		# Illumina format
		r_index = int(match.group(3))-1
		name = match.group(2)
		if not pairs.get(name):
		    pairs[name] = [None,None]
		pairs[name][r_index] = file_path
	else:
	    print "Error", file_path, "not in Illumina format"
	    sys.exit(1)
	    
print pairs	    


