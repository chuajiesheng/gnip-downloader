import sys, requests, yaml, os, subprocess

if len(sys.argv) < 2:
    print 'Please provide results.json URL.'
    exit(0)

url = sys.argv[1]
print 'Downloading', url

script_path = os.path.dirname(os.path.realpath(__file__))
credential_file = os.path.join(script_path, 'credential.yaml')
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

command_file = os.path.join(script_path, 'command.yaml')
print 'Reading', command_file, 'for commands to use'

with open(command_file, 'r') as stream:
    try:
        command = yaml.load(stream)
    except yaml.YAMLError as exc:
        exit(1)

working_directory = os.getcwd()
print 'Working directory', working_directory

gzip_directory = os.path.join(working_directory, 'gzipped')
print 'Downloading GZIP to directory', gzip_directory
if not os.path.exists(gzip_directory):
    os.makedirs(gzip_directory)

downloaded = 0

for url in urlList:
    cmd = [command['wget'], '--user=' + username, '--password=' + password, '--directory-prefix=' + gzip_directory, url]
    return_code = subprocess.call(cmd)
    assert return_code == 0
    downloaded += 1

assert downloaded == urlCount
