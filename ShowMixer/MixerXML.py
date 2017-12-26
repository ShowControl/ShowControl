'''
Created on Sun Dec  3 11:18:01 EST 2017
Create xml file that contains the mixerconsole object
for each mixer used by the project
@author: mac

'''

import sys
import inspect
import os
from os import path
import shutil
import uuid
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
import logging

import xml.dom.minidom as md
try:
    from lxml import ET
    print("running with lxml.etree")
except ImportError:
    import xml.etree.ElementTree as ET


pretty_print = lambda f: '\n'.join([line for line in md.parse(open(f)).toprettyxml(indent=' '*2).split('\n') if line.strip()])

class MixerConsoleXML():
    """"""
    def __init__(self, mixerconf_file, project_file):
        """"""
        logging.info('In MixerConsoleXML init')
        logging.info('Mixer definition file ' + mixerconf_file)
        logging.info('Project definition file ' + project_file)
        self.mxrstrips = {}
        self.mxrconsole = []
        self.mixerXML_element = ET.Element('showcontrol')
        self.mixers_element = ET.SubElement(self.mixerXML_element, 'mixers')
        ET.SubElement(self.mixers_element, 'version').text = '1.0'

        mixerdeftree = ET.parse(mixerconf_file)
        mixers = mixerdeftree.getroot()
        projecttree = ET.parse(project_file)
        projectroot = projecttree.getroot()
        equip_files = projectroot.findall("./project/equipment")
        project_mixers = []
        for equip_file in equip_files:
            fn = equip_file.get('href')
            logging.info(fn)
            eq_tree = ET.parse(cfgdict['configuration']['project']['folder'] + '/'+ fn)
            eq_root = eq_tree.getroot()
            f_mixer_elements = eq_root.findall("./equipment/mixers/mixer")
            for mxr in f_mixer_elements:
                project_mixers.append(mxr)
            pass
        for mixer in mixers:
            mfr = mixer.get('mfr')
            model = mixer.get('model')
            logging.info('Defined mixer: {} {}'.format(mfr, model))
        for mixer in mixers:
            mfr = mixer.get('mfr')
            model = mixer.get('model')
            for project_mixer in project_mixers:
                proj_mfr = project_mixer.find('./mfr').text
                proj_mod = project_mixer.find('./model').text
                if proj_mfr == mfr and proj_mod == model:
                    logging.info('Project is using {} {}'.format(proj_mfr, proj_mod))
                    stripattribs = self.BuildStrips(mixer)
                    # create the xml for this mixer
                    self.BuildMixerXML(mixer, project_mixer.get('uuid'))
                pass
        return

    def BuildStrips(self, mixer):
        self.mxrconsole = []
        s_countbase = mixer.find('countbase').text
        i_countbase = int(s_countbase.replace('\"', ''))
        firstchan = 1  # wonky way to fix issue with X32: CH1 >> 01, yamaha: CH1 is 0 offset from a midi value
        if i_countbase == 1:
            firstchan = 0
        strips = mixer.findall('strip')
        for strip in strips:
            stripattribs = strip.attrib
            self.mxrstrips[stripattribs['type']] = {}
            self.cntrlcount = int(stripattribs['cnt'])
            for x in range(i_countbase, self.cntrlcount + i_countbase):
                self.mxrconsole.append(
                    {'name': stripattribs['name'] + '{0:02}'.format(x + firstchan), 'type': stripattribs['type'],
                     'channum': x})
        return stripattribs

    def BuildMixerXML(self, consdef, cons_uuid):
        s_countbase = consdef.find('countbase').text
        i_countbase = int(s_countbase.replace('\"', ''))
        firstchan = 1  # wonky way to fix issue with X32: CH1 >> 01, yamaha: CH1 is 0 offset from a midi value
        if i_countbase == 1:
            firstchan = 0
        # mixer_element = ET.SubElement(self.mixers_element, 'mixer', {'uuid': '{}'.format(uuid.uuid4()), 'mfr': consdef.get('mfr')})
        mixer_element = ET.SubElement(self.mixers_element, 'mixer', {'uuid': cons_uuid, 'mfr': consdef.get('mfr')})

        for count, strip in enumerate(self.mxrconsole):
            strip_element = ET.SubElement(mixer_element, 'strip', {'uuid': '{}'.format(uuid.uuid4())})
            ET.SubElement(strip_element, 'name').text = strip['name']
            ET.SubElement(strip_element, 'type').text = strip['type']
            ET.SubElement(strip_element, 'channum').text = str(strip['channum'])
        return

    def write(self, newchars,  revision=True, filename=''):
        """save a new characters file.
        If revision is true, save with a revision number
        i.e. this essentially makes a backup of the config file,
        typically call with revision=True before an add or insert
        If revision=False, save
        in the file specified by filename"""
        newdoctree = ET.ElementTree(newchars)
        if filename == '':
            logging.debug('Configuration not saved, no filename provided!')
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText('Configuration not saved, no filename provided!')
            msgBox.exec_()
            return
        rev = 1
        oldroot, extension = path.splitext(filename)
        if revision:
            while path.isfile(oldroot + '-{0}'.format(rev) + extension):
                rev += 1
            shutil.copyfile(filename, oldroot + '-{0}'.format(rev) + extension)
            logging.debug('Configuration written to: ' + oldroot + '-{0}'.format(rev) + extension)
        filename_up = oldroot + '_up' + extension  # up >>> uglyprint
        newdoctree.write(filename_up, encoding="UTF-8", xml_declaration=True)
        of = open(filename, 'w')
        of.write(pretty_print(filename_up))
        of.close()

        logging.debug('Configuration written to: ' + filename)

        return


if __name__ == "__main__":
    HOME = os.path.expanduser("~")

    # CFG_DIR = HOME + '/.config/ShowControl'
    # CFG_PATH = CFG_DIR + '/ShowControl_config.xml'
    # LOG_DIR = HOME + '/.log/ShowControl'

    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    os.sys.path.insert(0, parentdir)
    from ShowControl.utils.ShowControlConfig import configuration, CFG_DIR, CFG_PATH, LOG_DIR

    logging.basicConfig(level=logging.INFO,
                        filename=LOG_DIR + '/MixerXML.log', filemode='w',
                        format='%(name)s %(levelname)s %(message)s')
    conf = configuration()
    cfgdict = conf.toDict()
    logging.info(str(cfgdict))
    projects_folder, project_name = os.path.split(cfgdict['configuration']['project']['folder'])
    mixerdefs_file = CFG_DIR + '/' + cfgdict['configuration']['mixers']['folder'] + '/' + cfgdict['configuration']['mixers']['file']
    project_file = cfgdict['configuration']['project']['folder'] + '/' + cfgdict['configuration']['project']['file']
    MCX = MixerConsoleXML(mixerdefs_file, project_file)
    MCX.write(MCX.mixerXML_element, True, cfgdict['configuration']['project']['folder'] + '/' + '{}_projectmixers.xml'.format(project_name))
    pass

