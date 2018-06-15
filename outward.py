#!/usr/bin/env python3
# encoding: utf-8 (as per PEP 263)

import sys
import os
import fileinput
import base64

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

        if key == 'dn':
            current_dn = full_value
            data[current_dn] = {}

        else:
            if not current_dn:
                raise Exception('Non-dn attribute "%s" while not inside a dn block!' % (key))

            if key not in data[current_dn]:
                data[current_dn][key] = []

            if len(full_value) < 500:
                data[current_dn][key] += [full_value]

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

                data[current_dn][key] += ['FILE=' + filename]

    print(data)


if __name__ == '__main__':
    main()
