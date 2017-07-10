#!/usr/bin/env python3
'''
Created July 2017

Attempt to normalize reading of xml files into dictionaries.
etree_to_dict kept for intersting stuff, but does not work not even close
etree_to_dict2 works for a ShowControl_config.xml, but won't work on much else
Have to focus on other stuff, but the should be looked at in future to eliminate rewrite of xml to dict for every xml file.
@author: mac
'''

import os
import sys
import inspect
from collections import Counter
from collections import defaultdict
from os import path
from PyQt5 import QtWidgets

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(currentdir)
syblingdir =  os.path.dirname(currentdir) + '/ShowControl/utils'
print(syblingdir)
parentdir = os.path.dirname(currentdir)
print(parentdir)
sys.path.insert(0,syblingdir)
print(sys.path)

try:
    from lxml import ET
except ImportError:
    import xml.etree.ElementTree as ET

HOME = os.path.expanduser("~")

CFG_DIR = HOME + '/.showcontrol'
CFG_PATH = CFG_DIR + '/ShowControl_config.xml'

def etree_to_dict2(t):
    gen_dict = {}
    t_root = t.getroot()
    t_iter = t_root.iter()

    root_elments = list(t_root)
    for level1_element in root_elments:
        print('level1 element: {}'.format(level1_element.tag))
        lev1_key = level1_element.tag
        lev1_children = list(level1_element)
        if lev1_children:
            lev1_value = {}
            for lev1_child in lev1_children:
                lev1_child_attrib = lev1_child.attrib
                if lev1_child_attrib:
                    attribvals = list(lev1_child_attrib.items())
                    lev1_child_key = '{}_{}={}'.format(lev1_child.tag, attribvals[0][0], attribvals[0][1])
                else:
                    lev1_child_key = lev1_child.tag
                lev2_elements = list(lev1_child)
                if lev2_elements:
                    lev2_value = {}
                    for lev2_element in lev2_elements:
                        lev2_value[lev2_element.tag] = lev2_element.text.strip()
                    lev1_value[lev1_child_key] = lev2_value
                else:
                    lev1_value[lev1_child_key] = lev1_child.text.strip()
        else:
            lev1_value = level1_element.text.strip()
        gen_dict[lev1_key] = lev1_value
    return gen_dict

def etree_to_dict(t):
    gen_dict = {}
    t_root = t.getroot()
    t_iter = t_root.iter()

    root_elments = list(t_root)
    for level1_element in root_elments:
        print('level1 element: {}'.format(level1_element.tag))

        # -------------------------------------
        # get a list of child elements and a count of duplicates
        level1_children = list(level1_element)
        element_names = []
        for ename in level1_children:
            element_names.append(ename.tag)
        counter = Counter(element_names).most_common() # this produces a list of elements and how many of each
        print(counter)
        counter_dict = todict(counter)
        # -------------------------------------
        dup_dict = {}
        for elname, count in counter:
            print(elname, count)
            # find all of each element
            allels = level1_element.findall(elname)
            # duplicates are supposed to have an ID attribute
            if len(allels) > 1:
                for dup in allels:
                    id = dup.get('id')
                    dup_dict[id] = {}
            else:
                nondup = level1_element.find(elname)
                dup_dict[nondup.tag] = nondup.text.strip()
            pass


        level1_dict ={}
        level2_dict = {}
        if level1_children: # this level1_element has children
            level1_child_dict = {}
            for level1_child in level1_children:
                print('\tlevel1 child tag: {0} text: {1}'.format(level1_child.tag, level1_child.text.strip()))
                level1_child_dict[level1_child.tag] = level1_child.text.strip()

                # check if this element is one of the duplicates
                child_count = counter_dict[level1_child.tag]
                if child_count > 1:  # this is one of duplicate element names and should have a an id attribute
                    child_attribs = level1_child.attrib
                    print('child attribs: {}'.format(child_attribs))
                level2_children = list(level1_child)
                print('\t\ttag: {0}'.format(level2_children))

                for level2_child in level2_children:
                    level2_dict[level2_child.tag] = {level2_child.tag : level2_child.text}
            gen_dict[level1_element.tag] = level1_child_dict
                #level1_dict[child_attribs['id']] = ''
        else:  # this element has no children
            # check for text and attributes
            level1_attribs = level1_element.attrib
            print('tag: {0} text: {1}'.format(level1_element.tag, level1_element.text.strip()))
            gen_dict[level1_element.tag] = level1_element.text.strip()
    for item in t_iter:
        itmtag = item.tag
        itmtxt = item.text.strip()
        itmatrb = item.attrib
        itmchildrn = list(item)
        print(itmtag, itmtxt, itmatrb)
    return 10

def todict( item ):
    cdict = {}
    for v, k in item:
        cdict[v] = k
    print(cdict)
    return cdict

if __name__ == "__main__":
    tree = ET.parse(CFG_PATH)
    d = etree_to_dict2(tree)
    tree = ET.parse('/home/mac/Shows (copy 1)/Pauline/MixerMap.xml')
    d = etree_to_dict2(tree)

    pass