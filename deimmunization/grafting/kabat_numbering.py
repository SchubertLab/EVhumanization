#!/usr/bin/env python
# encoding: utf-8
"""Module to call a web server to number a variable antibody domain accoring to
the Kabat numbering scheme.

Service at address: http://www.bioinf.org.uk/cgi-bin/abnum.

"""

import sys
from HTMLParser import HTMLParser
from urllib import urlopen
import argparse
from Bio import SeqIO
from collections import defaultdict


class SimpleTextParser(HTMLParser):

    """Simple HTML parser that joins encoutered data together."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.data = []

    def handle_data(self, data):
        self.data.append(data)


class KabatNumbering():

    """Call antibody Kabat numbering web server.

    Parameters
    ----------
    sequence : `SeqRecord`
        The antibody sequence to be numbered.

    Attributes
    ----------
    sequence : `SeqRecord`
        The antibody sequence that is numbered according to Kabat.
    kabat_list : list of tuple of length 2 (str, str)
        Kabat numbering, as list of tuples (Kabat identifier, residue).
    kabat_dict : dict (key=tuple of length 2 (int, str), value=int)
        Kabat numbering, as dictionary: key=(Kabat number, Kabat Character),
        value=residue number of the sequence.

    """

    def __init__(self, sequence):
        self.sequence = sequence
        abnum_url = ('http://www.bioinf.org.uk/cgi-bin/abnum/'
                     'abnum.pl?plain=1&aaseq=%s&scheme=-k') % sequence.seq

        kabat_parser = SimpleTextParser()
        try:
            kabat_parser.feed(urlopen(abnum_url).read())
        except IOError as e:
            sys.exit('%s: %s' % (e.strerror, e.filename))
        kabat_parser.close()

        self._rawdata = ''.join(kabat_parser.data)
        self.kabat_list = [(x[:-2], x[-1:]) for x in self._rawdata.split('\n')
                           if not x == '']

        self.kabat_dict = defaultdict(lambda: -1)
        res_num = 1
        for kabat, res in self.kabat_list:
            if not res == '-':
                kabat_key = (int(kabat[1:-1]), kabat[-1]) if kabat[-1].isalpha()\
                    else (int(kabat[1:]), '')
                self.kabat_dict[kabat_key] = res_num
                res_num += 1

    def __str__(self):
        return ('KabatNumbering [sequence=%s, kabat_list=%s, kabat_dict=%s]'
                % (self.sequence, self.kabat_list, self.kabat_dict))

    def to_file(self, out):
        """Write Kabat numbering of the provided sequence to file."""
        with open(out, 'w') as out_file:
            out_file.write('# Kabat numbering\n')
            out_file.write('# id: %s\n# name: %s\n# description: %s\n'
                           % (self.sequence.id, self.sequence.name,
                              self.sequence.description))
            out_file.write(''.join(self._rawdata))

    def to_stdout(self):
        """Write Kabat numbering of the provided sequence to stdout."""
        print >> sys.stderr, '# Kabat numbering'
        print >> sys.stderr, ('# id: %s\n# name: %s\n# description: %s'
                              % (self.sequence.id, self.sequence.name,
                                 self.sequence.description))
        print ''.join(self._rawdata)


def main():
    """Invoke wrapper for calling an antibody Kabat numbering web server."""
    if len(sys.argv[1:]) < 1 or len(sys.argv[1:]) > 2:
        sys.exit('python %s <sequence> [<out>]' % sys.argv[0])
    seq_record = SeqIO.read(sys.argv[1], 'fasta')

    kabat_numbering = KabatNumbering(seq_record)
    kabat_numbering.to_file(sys.argv[2]) if len(sys.argv[1:]) >= 2\
        else kabat_numbering.to_stdout()


if __name__ == '__main__':
    main()
