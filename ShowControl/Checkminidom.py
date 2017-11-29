from xml.dom import minidom
import xml.dom.minidom as md
from bs4 import BeautifulSoup
# try:
#     from lxml import ET
# except ImportError:
#     import xml.etree.ElementTree as ET
try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

pretty_print = lambda f: '\n'.join([line for line in md.parse(open(f)).toprettyxml(indent=' '*2).split('\n') if line.strip()])

class testpretty():
    def __init__(self, cuefilename):
        self.cuetree = etree.ElementTree(file=cuefilename)
        self.cuelist = etree.parse(cuefilename)
        self.cuelist_root = self.cuelist.getroot()
        someET = minidom.parseString(etree.tostring(self.cuelist_root, encoding="unicode", method="xml", short_empty_elements=True)).toprettyxml()
        otherET = BeautifulSoup(etree.tostring(self.cuelist_root, encoding="unicode", method="xml", short_empty_elements=True), "xml").prettify()

        return

class lxmltest():
    def __init__(self, cuefilename):
        self.cuetree = etree.ElementTree(file=cuefilename)
        self.cuelist = etree.parse(cuefilename)
        self.cuelist_root = self.cuelist.getroot()
        pps = etree.tostring(self.cuelist_root, pretty_print=True,)
        return


if __name__ == "__main__":
    #thing = testpretty('/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuesx.xml')
    #lxl = lxmltest('/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuesx.xml')

    print(pretty_print('/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuesx.xml'))
    of = open('/home/mac/SharedData/ShowSetups/Shows/Fiddler/testpp.xml', 'w')
    of.write(pretty_print('/home/mac/SharedData/ShowSetups/Shows/Fiddler/Fiddler_cuesx.xml'))
    of.close()
    pass