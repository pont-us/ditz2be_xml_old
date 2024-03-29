#!/usr/bin/python
# -*- coding: utf-8 -*-
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the original
# work is properly attributed to Matěj Cepl.
# The name of Matěj Cepl may be used to endorse or promote
# products derived from this software without specific prior
# written permission.
# This software is provided by Matěj Cepl "AS IS" and without any
# express or implied warranties.

import yaml
from xml.etree import ElementTree as et
import logging
import glob
import os.path
import io
logging.basicConfig(format='%(levelname)s:%(funcName)s:%(message)s',
                    level=logging.DEBUG)
DITZ_DIR = ".ditz/"


def _xml_indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem) != 0:
        if not (elem.text and elem.text.strip()):
            elem.text = i + "  "
        for e in elem:
            _xml_indent(e, level + 1)
        if not (e.tail and e.tail.strip()):
            e.tail = i
    else:
        if level and not(elem.tail and elem.tail.strip()):
            elem.tail = i


def make_comment(body, who, when):
    out = et.Element("comment")
    et.SubElement(out, "author").text = who
    et.SubElement(out, "date").text = when
    et.SubElement(out, "content-type").text = "text/plain"
    et.SubElement(out, "body").text = body
    return out


class Issue(yaml.YAMLObject):
    yaml_tag = "!ditz.rubyforge.org,2008-03-06/issue"

    def __init__(self, title, desc, type_val, component, release, reporter,
                 status, disposition, creation_time, references, id,
                 log_events):
        self.title = title
        self.desc = desc
        self.type = type_val
        self.component = component
        self.release = release
        self.reporter = reporter
        self.status = status
        self.disposition = disposition
        self.creation_time = creation_time
        self.references = references
        self.id = id
        self.log_events = log_events

    @staticmethod
    def __format_time(in_time):
        """
        in_time is datetime.datetime
        example: "2012-02-23T22:09:58Z"
        """
        logging.debug("in_time = %s", in_time)
        out = in_time.strftime("%a, %d %b %Y %H:%M:%S %z")
        logging.debug("out = %s, out")
        return out

    def __add_subelement(self, iss_attr, trg_elem, convert=None):
        if getattr(self, iss_attr) is not None:
            if convert:
                value = convert(getattr(self, iss_attr))
            else:
                value = getattr(self, iss_attr)
            logging.debug("iss_attr = %s, value = %s", iss_attr, value)
            et.SubElement(self.bug, trg_elem).text = value

    def to_XML(self):
        self.bug = et.Element("bug")

        self.__add_subelement("creation_time", "created",
                              self.__format_time)
        self.__add_subelement("title", "summary")
        self.__add_subelement("status", "status")
        self.__add_subelement("reporter", "reporter")
        self.__add_subelement("reporter", "creator")
        # FIXME
        #self.__add_subelement("assignee", "assigned")

        if self.desc is not None:
            self.bug.append(make_comment(self.desc,
                                         self.reporter,
                                         self.__format_time(
                                             self.creation_time)))

        #for comment in get_comments(cnf['git_user'], cnf['git_password'],
        #                            cnf['repo'], iss[u"number"]):
        #    self.bug.append(make_comment(comment[u"body"],
        #               comment[u"user"][u"login"],
        #               format_time(comment[u"updated_at"])))

        return self.bug

    def __str__(self):
        return "id = %s\ntitle: %s\ncreated: %s" % (self.id, self.title,
                                                    self.creation_time)


class Project(yaml.YAMLObject):
    yaml_tag = "!ditz.rubyforge.org,2008-03-06/project"

    def __init__(self, name, version, components, releases):
        self.name = name
        self.version = version
        self.components = []
        self.releases = releases

        for comp in components:
            self.components.append(yaml.load(comp))


class Component(yaml.YAMLObject):
    yaml_tag = "!ditz.rubyforge.org,2008-03-06/component"

    def __init__(self, name):
        self.name = name


def main():
    #out_xml = et.fromstring("""<be-xml>
    #    <version>
    #        <tag>bf52e18a</tag>
    #        <committer>W. Trevor King</committer>
    #        <date>2011-05-25</date>
    #        <revision>bf52e18aad6e0e8effcadc6b90dfedf4d15b1859</revision>
    #    </version>
    #</be-xml>""")

    out_xml = et.fromstring("""<be-xml>
        <version>
        </version>
    </be-xml>""")

    issue_files = glob.glob(os.path.join(DITZ_DIR, "issue*.yaml"))
    logging.debug("issue_files = %s", issue_files)

    for i_file in issue_files:
        issue = yaml.load(io.open(i_file))
        out_xml.append(issue.to_XML())

    _xml_indent(out_xml)
    print et.tostring(out_xml, "utf-8")


if __name__ == '__main__':
    main()
