import sys, requests, yaml, os, subprocess, multiprocessing


def get_cmd():
    output_file = os.path.join(data_directory, str(index) + '.json.gz')
    cmd = [command['wget'],
           '--user=' + username,
           '--password=' + password,
           '--output-document=' + output_file,
           '-q',
           url]
    return cmd


def call_cmd(cmd):
    status_code = subprocess.call(cmd)
    if status_code is 0:
        sys.stdout.write('.')
        sys.stdout.flush()
    return status_code


def make_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


if __name__ == '__main__':
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

    data_directory = os.path.join(working_directory, 'data')
    print 'Downloading to directory', data_directory
    make_directory(data_directory)

    cmd_list = []
    for index, url in enumerate(urlList):
        cmd = get_cmd()
        cmd_list.append(cmd)

    results = []
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(call_cmd, cmd_list)
    pool.close()
    pool.join()

    for index, result in enumerate(results):
        if result is not 0:
            print 'Check [{}] {}'.format(index, urlList[index])

    files = []
    for (dirpath, dirnames, filenames) in os.walk(data_directory):
        files.extend(filenames)
        break

    cmd = [command['unzip'], '-r', '-k', data_directory]
    print 'Unzipping all file in', data_directory
    return_code = subprocess.call(cmd)
    assert return_code == 0

    json_directory = os.path.join(working_directory, 'json')
    make_directory(json_directory)
    cmd = '{} -f {} {}'.format(command['move'], data_directory + os.path.sep + '*.json', json_directory)
    print cmd
    print 'Moving json files to', json_directory
    return_code = subprocess.call(cmd, shell=True)
    assert return_code == 0
