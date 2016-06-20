import os, json, sys


def is_json(line):
    try:
        json.loads(line)
    except ValueError, e:
        return False
    return True


def valid_gnip_json_file(filename):
    valid_lines = 0
    last_line = ''

    with open(filename) as f:
        for line in f:
            if len(line.strip()) < 1:
                continue

            last_line = line
            if is_json(line):
                valid_lines += 1

    json_checksum = json.loads(last_line)
    if 'info' in json_checksum and 'activity_count' in json_checksum['info']:
        activity_count = json_checksum['info']['activity_count']
        expected_count = valid_lines - 1
        if activity_count == expected_count:
            return True

    return False

if __name__ == '__main__':
    working_directory = os.getcwd()
    print 'Working directory', working_directory

    json_directory = os.path.join(working_directory, 'json')
    files = []
    for (dirpath, dirnames, filenames) in os.walk(json_directory ):
        files.extend(filenames)
        break

    verified = 0
    for index, f in enumerate(files):
        if valid_gnip_json_file(os.path.join(json_directory, f)):
            sys.stdout.write('.')
            sys.stdout.flush()
            verified += 1
        else:
            sys.stdout.write('[{}]'.format(index))
            sys.stdout.flush()

    print '{} of {} correct'.format(verified, len(files))
