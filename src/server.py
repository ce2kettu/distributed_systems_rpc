from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xml.etree.ElementTree as ET
import config
import requests
from os import path
from datetime import datetime

# Restrict to a particular path.


class SimpleThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ("/RPC2",)


def create_note(topicEl, topicName, description):
    if (not topicEl):
        topicEl = ET.Element("topic")
        topicEl.set("name", topicName)

    note = ET.SubElement(topicEl, "note")
    textEl = ET.SubElement(note, "text")
    textEl.text = description
    timestamp = ET.SubElement(note, "timestamp")
    timestamp.text = str(datetime.now())
    return topicEl


def insert_note(topicName, description):
    # database does not exist yet
    if (not path.exists(config.XML_NAME)):
        root = ET.Element("data")
        tree = ET.ElementTree(root)
        tree.write(config.XML_NAME)

    tree = ET.parse(config.XML_NAME)
    root = tree.getroot()
    topicEl = None

    # check if the topic already exists
    for topic in root.findall("topic"):
        if (topic.get("name") == topicName):
            topicEl = topic
            break

    if (topicEl):
        # modify existing note
        topicEl = create_note(topicEl, topicName, description)
    else:
        # append new topic with note inside
        root.append(create_note(topicEl, topicName, description))

    # save file
    tree.write(config.XML_NAME)
    return True


def find_notes(topicName):
    topics = []

    if (path.exists(config.XML_NAME)):
        tree = ET.parse(config.XML_NAME)
        root = tree.getroot()

        # find all notes within a topic
        for note in root.findall(f"./topic[@name='{topicName}']/note"):
            text = note.find("text").text
            timestamp = note.find("timestamp").text
            topics.append((text, timestamp))

    return topics

def enrich_topic(topicName, searchTerm):
    session = requests.Session()
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "namespace": "0",
        "search": searchTerm,
        "limit": "1",
        "format": "json"
    }

    req = session.get(url=url, params=params)
    data = req.json()
    links = data[3]

    # some link found
    if (len(links) != 0):
        if (path.exists(config.XML_NAME)):
            tree = ET.parse(config.XML_NAME)
            root = tree.getroot()
            topic = root.find(f"./topic[@name='{topicName}']")

            # topic exists
            if (topic):
                topic.set('link', links[0])
                tree.write(config.XML_NAME)
                return True

    return False


# Create server
with SimpleThreadXMLRPCServer((config.HOST, config.PORT), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    server.register_function(find_notes, "find")
    server.register_function(insert_note, "insert")
    server.register_function(enrich_topic, "enrich")

    # Run the server's main loop
    server.serve_forever()
