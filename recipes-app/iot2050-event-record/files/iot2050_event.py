#!/usr/bin/env python3
#
# Copyright (c) Siemens AG, 2023
#
# Authors:
#  Li Hua Qian <huaqian.li@siemens.com>
#
# SPDX-License-Identifier: MIT
#
import json
from systemd import journal
from iot2050_event_global import iot2050_event_identifier

def write_event(event_type, event):
    if not event:
        raise EventIOError("Empty Events: no events to write")
    journal_stream = journal.stream(iot2050_event_identifier)
    log_to_record = event_type + ": " + event
    journal_stream.write(log_to_record)

def read_all_events(journal_reader):
    events = []
    for entry in journal_reader:
        events.append(entry['MESSAGE'])
    events_str = json.dumps(events, indent=4)

    return events_str

def read_specified_event(event_type, journal_reader):
    events = []
    for entry in journal_reader:
        if event_type in entry['MESSAGE']:
            events.append(entry['MESSAGE'])
    events_str = json.dumps(events, indent=4)

    return events_str

def read_event(event_type):
    journal_reader = journal.Reader()
    journal_reader.add_match("SYSLOG_IDENTIFIER={}".format(iot2050_event_identifier))

    if not event_type:
        return read_all_events(journal_reader)
    else:
        return read_specified_event(event_type, journal_reader)

class EventIOError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
