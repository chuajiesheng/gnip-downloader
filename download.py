import sys, requests, yaml

if len(sys.argv) < 2:
    print 'Please provide results.json URL.'
    exit(0)

url = sys.argv[1]
print 'Downloading', url

credential_file = 'credential.yaml'
print 'Reading', credential_file, 'for HTTP credential'

with open(credential_file, 'r') as stream:
    try:
        credential = yaml.load(stream)
    except yaml.YAMLError as exc:
        exit(1)

username = credential['username']
password = credential['password']
print 'Using', username

r = requests.get(url, auth=(username, password))
assert r.status_code == 200

data = r.json()
urlCount = data['urlCount']
urlList = data['urlList']

assert urlCount == len(urlList)
print 'Number of URL:', urlCount
