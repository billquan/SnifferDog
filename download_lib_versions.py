import json
import sys
import os
import requests
import wget
import tarfile
import argparse
import multiprocessing
from time import sleep

#invalid_suffixes = ('.exe', '.whl')
invalid_suffixes = ('.exe')
data_dir = '/data/sda/pypi_libs'
counter = multiprocessing.Value('i', 0)
def single_package(package_name):
    global counter
    with counter.get_lock():
        counter.value += 1
    print("counter.value:", counter.value)
    sleep(1)
    url = "https://pypi.python.org/pypi/{}/json".format(package_name)
    r = requests.get(url)
    print(r)
    if r.status_code != 200:
        print("failed to fetch {}".format(package_name))
        return 0
    working_dir = os.path.join(os.path.join(data_dir, package_name))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    data = json.loads(r.text)
    versions = data["releases"].keys()
    for v in versions:
        urls = [ele['url'] for ele in data["releases"][v]]
        new_dir = os.path.join(working_dir, v)
        if not os.path.exists(new_dir):
            os.mkdir(new_dir)
        for url in urls:
            if url.endswith(invalid_suffixes):
                continue
            file_name = url.rsplit('/', 1)[-1]
            if os.path.exists(os.path.join(new_dir, file_name)):
                continue
            wget.download(url, os.path.join(new_dir))

def main():
    #single_package("requests")
    #package_name = sys.argv[1]
    '''
    with open('lib_names.txt') as f:
        for i in range(2):
            package_name = f.readline().rstrip()
            single_package(package_name)
    '''

    parser = argparse.ArgumentParser(
        description="download all versions of a library")
    parser.add_argument('path', metavar='lib_name_list', type=str,
                        help='The path to the list of library names')
    parser.add_argument('-n', metavar='parallel_number', type=str,
                        help='The number of parallel works, default is 15', default=15)

    args = parser.parse_args()
    path = args.path
    number = int(args.n)
    with multiprocessing.Pool(processes=number) as pool:
        with open(path) as f:
            name_list = f.read().splitlines()[:2000]
        pool.map(single_package, iter(name_list))

if __name__ == '__main__':
    main()
