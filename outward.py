#!/usr/bin/env python3
# encoding: utf-8 (as per PEP 263)

import sys
import os
import fileinput
import base64
import string

"""
Final structure:
    dict(
        uid=doej,ou=people,dc=example: {
            cn: ['John Doe',],
            email: ['doej@fim.uni-passau.de', 'johndoe@gmail.com'],
        }
"""

class filepeek(object):
    def __init__(self):
        self.fi = fileinput.input()
        try:
            self.next_elem = self.fi.__next__().rstrip('\n')
        except StopIteration:
            self.next_elem = None

    def next(self):
        elem = self.next_elem
        try:
            self.next_elem = self.fi.__next__().rstrip('\n')
        except StopIteration:
            self.next_elem = None
        return elem

    def peek(self):
        return self.next_elem

def main():
    data = {}
    attrs = set()
    charset = set()
    current_dn = ''
    fp = filepeek()
    while True:
        line = fp.next()
        if line is None:
            break

        if not line:
            # end of dn block
            current_dn = ''
            continue

        if line.lstrip().startswith('#'):
            # skip comment line
            continue

        if line.startswith('version: '):
            # skip version line
            continue

        key, value = line.split(': ', 1)
        is_b64 = key.endswith(':')
        key = key.rstrip(':')

        full_value = value
        while fp.peek().startswith(' '):
            full_value += fp.next()[1:]

        if is_b64:
            full_value = base64.b64decode(full_value)

        attrs.add(key)

        if key == 'dn':
            current_dn = full_value
            data[current_dn] = {}

        if not current_dn:
            raise Exception('Non-dn attribute "%s" while not inside a dn block!' % (key))

        if key not in data[current_dn]:
            data[current_dn][key] = []

        if len(full_value) < 500:
            if type(full_value) is bytes:
                full_value = full_value.decode('utf8')

            store_value = full_value

        else:
            # too large for CSV output, write to file instead

            # find unused filename
            fileid = 0
            while True:
                filename = 'dn=%s,attr=%s,id=%d' % (current_dn, key, fileid)
                if not os.path.exists(filename):
                    break
                fileid += 1

            with open(filename, 'wb') as f:
                f.write(full_value)

            store_value = 'FILE=' + filename

        data[current_dn][key] += [store_value]
        charset.update(set(store_value))

    usable_chars = set(string.printable) - set(string.whitespace)
    available_chars = usable_chars - charset
    sys.stderr.write('The following characters DO NOT appear in the dataset (i.e. they can be freely used as separators etc):\n')
    sys.stderr.write('%s\n' % (' '.join(sorted(available_chars))))

    separator = ';'
    joiner = '|'
    strdelimiter = '"'

    attrs = list(sorted(attrs))

    first = True
    for attr in attrs:
        if not first:
            sys.stdout.write(separator)
        sys.stdout.write(attr)
        first = False

    sys.stdout.write('\n')

    for entry in data:
        first = True
        for attr in attrs:
            if not first:
                sys.stdout.write(separator)
            if attr in data[entry]:
                sys.stdout.write(strdelimiter)
                sys.stdout.write(
                        joiner.join(
                            data[entry][attr]
                        )
                )
                sys.stdout.write(strdelimiter)
            first = False
        sys.stdout.write('\n')


if __name__ == '__main__':
    main()
