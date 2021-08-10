import subprocess
from exception import CommandException


def parse_pip_list(output):
    output_line = output.split('\n')
    output_line = output_line[2:]
    pkg = [p.split(' ')[0] for p in output_line ]
    return pkg


def parse_pip_show(output):
    output_line = output.split('\n')
    pkg_info = {}
    for line in output_line:
        index = line.find(':')
        key, val = line[:index], line[index+1:]
        pkg_info[key]=val
    return pkg_info


def get_all_package():
    command = 'pip list'
    status, output = subprocess.getstatusoutput(command)
    if status == 0:
        return parse_pip_list(output)
    else:
        error = "some errors occured when run command {}".format(command)
        print(error)
        raise CommandException(error)


def get_package_info(pkg):
    command = 'pip show {}'.format(pkg)
    print('running command: {}'.format(command))
    status, output = subprocess.getstatusoutput(command)
    if status == 0:
        return parse_pip_show(output)
    else:
        error = "some errors occured when run command {}".format(command)
        print(error)
        raise CommandException(error)
