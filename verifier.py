import os, json, sys


class GnipDataFile:
    @staticmethod
    def is_json(line):
        try:
            json.loads(line)
        except ValueError, e:
            return False
        return True

    def __init__(self, filename):
        self.filename = filename
        self.activity_count = 0

    def is_valid(self):
        valid_lines = 0
        last_line = ''

        with open(self.filename) as f:
            for line in f:
                if len(line.strip()) < 1:
                    continue

                last_line = line
                if self.is_json(line):
                    valid_lines += 1

        json_checksum = json.loads(last_line)
        if 'info' in json_checksum and 'activity_count' in json_checksum['info']:
            self.activity_count = json_checksum['info']['activity_count']
            expected_count = valid_lines - 1
            if self.activity_count == expected_count:
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
    data_lines = 0
    for index, f in enumerate(files):
        gnip_file = GnipDataFile(os.path.join(json_directory, f))
        if gnip_file.is_valid():
            sys.stdout.write('.')
            sys.stdout.flush()
            verified += 1
            data_lines += gnip_file.activity_count
        else:
            sys.stdout.write('[{}]'.format(index))
            sys.stdout.flush()

    print '{} of {} correct'.format(verified, len(files))
    print '{} activity count'.format(data_lines)
