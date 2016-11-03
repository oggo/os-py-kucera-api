'''
Created on 06.10.2016

@author: oggo
'''
import re, os, argparse
import sys


#parse input args and params
argParser= argparse.ArgumentParser(description='js decorator for kucera html files')
argParser.add_argument('-td', action='store', dest='targetDir', help='name of the target directory')
# argParser.add_argument('-p', action='store', dest='portfolio', help='name of the portfolio')
argParser.add_argument('-v', action='version', version='%(prog)s 0.1')

args= argParser.parse_args()

class HtmlDecorator(object):
  '''Parses specific html documents and decorates them with configured templates'''

  homePath = "/home/oggo/software/dev/projects/python/bbKucera/src"
  htmlTagFinder = re.compile(r'(.*)</body>(.*)', re.DOTALL)
  ajaxRestCallTemplate = homePath + "/../decoratorTemplates/ajaxRestCallTemplate.tmpl"

  def __init__(self):
    print "decorator initialized!"  

  def decorateAjaxRestCall(self, pFile2Decorate):
    print "DEBUG: file to decorate is: {}".format(pFile2Decorate)
    fileText = open(pFile2Decorate).read()
    fileTuned = open(pFile2Decorate, 'w')
    text2Write= open(self.ajaxRestCallTemplate).read()

    #print "DEBUG: text is: {}".format(text2Write)
    match = self.htmlTagFinder.match(fileText)
    if None != match and None != match.group(1):
      print "DEBUG: group 1 is: {}".format(match.group(1))
      fileTuned.write(match.group(1))
      fileTuned.write("</body>")
      fileTuned.write(text2Write)
      print "DEBUG: group 2 is: {}".format(match.group(2))
      fileTuned.write(match.group(2))
    else:
      print "WARN: no match found for: {}".format(self.htmlTagFinder)

if __name__ == "__main__":
  decorator= HtmlDecorator()
#   targetDir= "/home/oggo/software/dev/projects/python/bbKucera/test"
  targetDir= os.getcwd()
  print "DENUG: cwd is: {}".format(targetDir)
  if None != args.targetDir:
    targetDir= args.targetDir
  print "DENUG: td is: {}".format(targetDir)
  for currFile in os.listdir(targetDir):
    fullName = os.path.join(targetDir, currFile)
    if os.path.isfile(fullName) and ".html" == os.path.splitext(fullName)[1]:
      try:
        decorator.decorateAjaxRestCall(fullName)
      except:
        e = sys.exc_info()[0]
        print "ERROR: error occured: {}".format(e)

