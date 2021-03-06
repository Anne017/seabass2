"""Helpers for build utils"""

import subprocess
import shlex
import re
from os import environ
from .config import CONTAINER_ID, CONTAINER_NAME

def shell_exec(command_string, cwd):
    """
    Executes given subprocess, returns iterable list of stdout lines

    Keyword arguments:
    command_string -- cmd string to execute
    """
    cmd_args = shlex.split(command_string)
    process = subprocess.Popen(cmd_args,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True,
                               cwd=cwd)

    for stdout_line in iter(process.stdout.readline, ''):
        yield strip_color(stdout_line)
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command_string)

def get_create_cmd():
    """Returns cmd string to create Seabass Libertine container"""
    return 'libertine-container-manager create -i {} -n "{}" -t chroot'\
        .format(CONTAINER_ID, CONTAINER_NAME)

def get_install_clickable_cmd():
    """Returns cmd string to install clickable into a Seabass Libertine container"""
    return 'libertine-launch -i {} \
            pip3 install --user git+https://gitlab.com/clickable/clickable.git'\
        .format(CONTAINER_ID)

def get_run_clickable_cmd(config_file):
    """Returns cmd string to run clickable from a Seabass Libertine container"""
    return 'libertine-launch -i {} clickable --container-mode --config={}'\
        .format(CONTAINER_ID, config_file)

def get_delete_desktop_files_cmd():
    """Returns cmd string to delete unneeded .desktop files from build container"""
    return 'libertine-launch -i {} rm /usr/share/applications/*.desktop'\
        .format(CONTAINER_ID)

def patch_env():
    """
    Sets TMPDIR var to existing /tmp directory.
    Prevents issues with various Libertine commands
    """
    environ['TMPDIR'] = '/tmp'

def strip_color(s): # pylint: disable=invalid-name
    """
    Remove ANSI color/style sequences from a string. The set of all possible
    ANSI sequences is large, so does not try to strip every possible one. But
    does strip some outliers seen not just in text generated by this module, but
    by other ANSI colorizers in the wild. Those include `\x1b[K` (aka EL or
    erase to end of line) and `\x1b[m`, a terse version of the more common
    `\x1b[0m`.

    from: https://github.com/jonathaneunice/colors
    """
    return re.sub('\x1b\\[(K|.*?m)', '', s)
