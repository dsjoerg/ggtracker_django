#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import binascii

import sc2reader
from sc2reader.utils import get_files
from sc2reader.exceptions import ReadError

def doFile(filename, arguments):
    '''Prints all events in SC2 replay file'''

    try:
        replay = sc2reader.read_file(filename, debug=True)
#        replay = sc2reader.read_file(filename, debug=True, apply=True)
    except ReadError as e:
        prev = e.game_events[-1]
        print "\nVersion {0} replay:\n\t{1}".format(e.replay.release_string, e.replay.filename)
        print "\t{0}, Type={1:X}, Code={2:X}".format(e.msg, e.type,e.code)
        print "\tPrevious Event: {0}".format(prev.name)
        print "\t\t"+prev.bytes.encode('hex')
        print "\tFollowing Bytes:"
        print "\t\t"+e.buffer.read_range(e.location,e.location+30).encode('hex')
        print "Error with '{0}': ".format(filename)
        print e
        return
    except TypeError as e:
        print "Error with '%s': " % filename,
        print e
        return
    except ValueError as e:
        print "Error with '%s': " % filename,
        print e
        return

    data = sc2reader.config.build_data[replay.build]
    print data

    if hasattr(arguments, "n"):
        events_to_print = replay.events[1:arguments.n]
    else:
        events_to_print = replay.events

    for event in events_to_print:
        event.apply(data)
        print event, binascii.hexlify(event.bytes)

    print

def main():
    parser = argparse.ArgumentParser(description='Prints all events from SC2 replay files or directories.')
    parser.add_argument('paths', metavar='filename', type=str, nargs='+',
                        help="Paths to one or more SC2Replay files or directories")
    parser.add_argument('-n', metavar='numevents', type=int,
                        help="Number of events to read")
    arguments = parser.parse_args()

    print arguments.n

    for path in arguments.paths:
        files = get_files(path, depth=0)

        for file in files:
            print "\n--------------------------------------\n{0}\n".format(file)
            doFile(file, arguments)

if __name__ == '__main__':
    main()
