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
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    cmd_list = []
    for index, url in enumerate(urlList):
        cmd = get_cmd()
        cmd_list.append(cmd)

    results = []
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(subprocess.call, cmd_list)
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
    return_code = subprocess.call(cmd)
    assert return_code == 0
