#!/usr/bin/env python

import getpass
import os
import subprocess
import sys

PASSWD_FILE = '/var/www/.htpasswd'
GROUPS_FILE = '/var/www/.htgroups'

def usage(progname):
    sys.stdout.write('Usage: %s [directory]\n' % progname)
    sys.stdout.write(' Create a .htaccess to protect a web directory.\n')

def check_home():
    """
    Check to see if the user has a ~/.htpasswd and if not set one up.
    """
    htpasswd = os.path.join(os.getenv('HOME'), '.htpasswd')
    if os.path.exists(htpasswd):
        return

    sys.stdout.write('You do not have a web password configured (%s).\n' % \
        htpasswd)
    password = getpass.getpass('Enter a password to set: ')

    if subprocess.check_call(['htpasswd', '-cb', htpasswd, getpass.getuser(), \
            password]):
        # Call failed.
        sys.stderr.write('Failed to create %s.\n' % htpasswd)
        sys.exit(1)

def main():
    # The directory to secure.
    webpath = None

    # Parse command line arguments.
    if len(sys.argv) == 1:
        webpath = os.getcwd()
    elif len(sys.argv) > 2:
        usage(sys.argv[0])
        return -1
    elif sys.argv[1] == '--help':
        usage(sys.argv[0])
        return 0
    else:
        webpath = os.path.abspath(sys.argv[1])

    if not os.path.exists(webpath):
        sys.stderr.write('%s does not exist.\n' % webpath)
        return -1

    htaccess = os.path.join(webpath, '.htaccess')
    if os.path.exists(htaccess):
        sys.stderr.write('%s already exists.\n' % htaccess)
        return -1

    check_home()

    # Open groups and passwd files we'll need later.
    passwd = None
    try:
        passwd = open(PASSWD_FILE, 'r')
    except:
        sys.stderr.write('Failed to open %s. Contact your administrator.\n' % \
            PASSWD_FILE)
        return -1
    groups = None
    try:
        groups = open(GROUPS_FILE, 'r')
    except:
        sys.stderr.write('Failed to open %s. Contact your administrator.\n' % \
            GROUPS_FILE)
        return -1

    # TODO: It would be better to use "AuthType Digest", but our Apache config
    # doesn't currently support this and it's a little complicated to setup.
    contents = 'AuthType Basic\n'

    # Use the location as the realm so that anything under this path is
    # automatically authenticated the same way, but no other paths are.
    contents += 'AuthName "%s"\n' % webpath

    # Use the same group and user's files for all .htaccess. These are
    # automatically generated and match the system's users and groups.
    contents += 'AuthUserFile %s\nAuthGroupFile %s\n' % \
        (PASSWD_FILE, GROUPS_FILE)

    while True:
        sys.stdout.write('Select an authentication mode:\n')
        sys.stdout.write(' 1. Allow access to any authenticated user\n')
        sys.stdout.write(' 2. Restrict access to a single user\n')
        sys.stdout.write(' 3. Restrict access to a single group\n')
        sys.stdout.write(' q. Canel and exit\n')
        sys.stdout.write('>')
        c = sys.stdin.readline().strip()
        if c == '1':
            access = 'Require valid-user\n'
        elif c == '2':
            access = 'Require user '
        elif c == '3':
            access = 'Require group '
        elif c == 'q':
            passwd.close()
            groups.close()
            return 0
        else:
            continue
        break

    if access == 'Require user ':
        users = map(lambda x:x.split(':')[0], filter(None, passwd.readlines()))
        while True:
            sys.stdout.write('Enter a user to allow:\n')
            sys.stdout.write('Valid users are: %s\n' % ' '.join(users))
            sys.stdout.write('>')
            c = sys.stdin.readline().strip()
            if c in users:
                access += '%s\n' % c
                break
    elif access == 'Require group ':
        grps = map(lambda x:x.split(':')[0], filter(None, groups.readlines()))
        while True:
            sys.stdout.write('Enter a group to allow:\n')
            sys.stdout.write('Valid groups are: %s\n' % ' '.join(grps))
            sys.stdout.write('>')
            c = sys.stdin.readline().strip()
            if c in grps:
                access += '%s\n' % c
                break

    contents += access

    try:
        f = open(htaccess, 'w')
        f.write(contents)
        f.close()
    except:
        sys.stderr.write('Failed to write %s.\n' % htaccess)

    sys.stdout.write('%s created.\n' % htaccess)
    return 0

if __name__ == '__main__':
    sys.exit(main())
