import xml.sax
import json

from coroutine import coroutine


class EventHandler(xml.sax.ContentHandler):
    def __init__(self, target):
        self.target = target

    def startElement(self, name, attrs):
        self.target.send(('start', (name, attrs._attrs)))

    def characters(self, content):
        self.target.send(('content', content))

    def endElement(self, name):
        self.target.send(('end', name))


@coroutine
def buses_to_dicts(target):
    while True:
        event, value = yield
        # Look for the start of a <bus> element
        if event == 'start' and value[0] == 'bus':
            busdict = {}
            fragments = []
            # Capture text of inner elements in a dict
            while True:
                event, value = yield
                if event == 'start':
                    fragments = []
                elif event == 'content':
                    fragments.append(value)
                elif event == 'end':
                    if value != 'bus':
                        busdict[value] = ''.join(fragments)
                    else:
                        target.send(busdict)
                        break


@coroutine
def filter_on_field(fieldname, value, target):
    while True:
        d = yield
        if d.get(fieldname) == value:
            target.send(d)


@coroutine
def bus_locations():
    while True:
        bus = yield
        print('{route},{id},"{direction}","{latitude},{longitude}"'.format(**bus))


if __name__ == '__main__':
    xml.sax.parse(
        "allroutes.xml",
        EventHandler(
                   buses_to_dicts(
                   filter_on_field("route", "22",
                   filter_on_field("direction", "North Bound",
                   bus_locations())))
              ))
