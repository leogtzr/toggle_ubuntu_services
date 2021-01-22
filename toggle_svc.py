#!/usr/bin/python3

import inquirer
import os
import subprocess
import re
import sys

from inquirer.themes import GreenPassion


class Service:
    """
        Creates a Service
    """

    def __init__(self, name, enabled=False):
        self.name = name
        self.enabled = enabled

    def __str__(self):
        if self.enabled:
            return f"🟢 {self.name}"
        else:
            return f"🔴 {self.name}"


def is_root():
    return os.geteuid() == 0


def change_service_status(svc):
    cmd = ['service', svc.name, 'stop' if svc.enabled else 'start']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)

    _, e = proc.communicate()

    if proc.returncode != 0:
        print("error disabling service status", file=sys.stderr)
        print(e.decode('ascii'), file=sys.stderr)


def get_services_from_cmd_output(cmd_output):
    services = []

    for line in cmd_output.splitlines():
        service_info_search = re.search(
            r"^\s*\[(.*)\]\s+(.*)$", line, re.IGNORECASE)
        if service_info_search:
            service_name = service_info_search.group(2)
            service_status = '+' in service_info_search.group(1)
        services.append(Service(service_name, service_status))

    return services


if not is_root():
    print("you are not root", file=sys.stderr)
    sys.exit(1)


cmd = ['service', '--status-all']
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

o, e = proc.communicate()

if proc.returncode != 0:
    print("error checking services status", file=sys.stderr)
    print(e.decode('ascii'), file=sys.stderr)
    sys.exit(1)


services = get_services_from_cmd_output(o.decode('ascii'))

questions = [inquirer.Checkbox(
    'selected_services',
    message="What are you interested in?",
    choices=services
)]

services_to_disable = inquirer.prompt(questions, theme=GreenPassion())

print('The following services will be changed:\n')
for service in services_to_disable['selected_services']:
    print("{0} will be {1}".format(service.name,
                                   "disabled" if service.enabled else "enabled"))

questions = [
    inquirer.Confirm('continue',
                     message="Continue", default=True)
]

print()

user_answer = inquirer.prompt(questions)
if user_answer['continue']:
    for service in services_to_disable['selected_services']:
        change_service_status(service)
