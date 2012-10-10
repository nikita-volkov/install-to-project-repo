#!/usr/bin/python

# Install to Project Repo
# A script for installing jars to an in-project Maven repository. 
# v0.1.1
# 
# MIT License
# (c) 2012, Nikita Volkov. All rights reserved.
# http://github.com/nikita-volkov/install-to-project-repo
# 


import os
import re
import shutil


def jars(dir):
  return [dir + "/" + f for f in os.listdir(dir) if f.lower().endswith(".jar")]

def parse_by_eclipse_standard(path):
  file = os.path.splitext(os.path.basename(path))[0]
  match = re.match("([\w\.]+)_(\d+\.\d+\.\d+.*)", file)
  if match != None:
    (name, version) = match.group(1, 2)

    name = name.split(".")
    source = name[-1] == "source"
    (group, name) = (".".join(name[:-2]), name[-2]) if source else (".".join(name[:-1]), name[-1])

    snapshot = version.upper().endswith(".SNAPSHOT")
    if snapshot:
      version = version[:-len(".snapshot")]

    return {
      "group": group,
      "name": name,
      "version": version,
      "snapshot": snapshot,
      "source": source
    }

def maven_dependencies(parsing_results):
  def artifact(parsing):
    return {
      "groupId": parsing["group"], 
      "artifactId": parsing["name"],
      "version": parsing["version"] + ("-SNAPSHOT" if parsing["snapshot"] else "")
    }
  def maven_dependency(artifact):
    return """
<dependency>
  <groupId>%(groupId)s</groupId>
  <artifactId>%(artifactId)s</artifactId>
  <version>%(version)s</version>
</dependency>
""" % artifact
  def unique_artifacts():
    artifacts = []
    for (_, parsing) in parsing_results:
      a = artifact(parsing)
      if a not in artifacts:
        artifacts.append(a)
    return artifacts

  return "\n".join([maven_dependency(a).strip() for a in unique_artifacts()])


def install(path, parsing):
  os.system(
    "mvn install:install-file" + \
    " -Dfile=" + path + \
    " -DgroupId=" + parsing["group"] + \
    " -DartifactId=" + parsing["name"] + \
    " -Dversion=" + parsing["version"] + ("-SNAPSHOT" if parsing["snapshot"] else "") + \
    " -Dpackaging=jar" + \
    " -DlocalRepositoryPath=repo" + \
    " -DcreateChecksum=true" + \
    (" -Dclassifier=sources" if parsing["source"] else "")
  )


def splits(str, splitter):
  parts = str.split(splitter)
  def split(i):
    (l, r) = splitAt(parts, i) 
    return (splitter.join(l), splitter.join(r))

  return map(split, range(1, len(parts)))

def splitAt(list, i):
  if i <= 0:
    return ([], list)
  elif i >= len(list):
    return (list, [])
  else:
    return (list[:i], list[i:])

def name_to_version_alternatives(filename):
  return [
    (n, v) 
    for (n, v) in splits(filename, "-") + splits(filename, "_")
    if v.lower() not in ["sources", "src", "snapshot"]
  ]

def group_to_name_alternatives(group):
  return [
    (n, v)
    for (n, v) in splits(group, ".")
    if (v.lower()) not in ["source", "snapshot"]
  ]

def version_parsing(version):

  def f(version, splitter, ending):
    parts = version.split(splitter)
    if parts[-1] == ending:
      return (splitter.join(parts[:-1]), True)
    else:
      return (version, False)

  (version, source) = f(version, "-", "sources")
  (version, snapshot) = f(version, "-", "SNAPSHOT")
  if not snapshot:
    (version, snapshot) = f(version, ".", "SNAPSHOT")

  return version, snapshot, source

def name_parsing(name):
  if name.endswith(".source"):
    return name[:-len(".source")], True
  else:
    return name, False

def unzip(l): 
  return tuple(zip(*l))

def input_choice(labels, values):
  for (i, v) in enumerate(labels):
    print "%d) %s" % (i+1, v)
  while True:
    try:
      i = raw_input()
      i = int(i)
      return values[i-1]
    except ValueError:
      print "Incorrect input: `%s` is not a number. Try again" % i
    except IndexError:
      print "Incorrect input: `%s` is out of range. Try again" % i


def parse_interactively(path):
  filename = os.path.splitext(os.path.basename(path))[0]

  print "-----"
  print "Processing `%s`" % path

  alternatives = name_to_version_alternatives(filename)
  alternatives.sort(key=lambda (n, v): len(v), reverse=True)

  if not alternatives:
    print "Incorrect name format: `%s`. Skipping" % filename
    return
  if len(alternatives) > 1:
    print "Choose a correct version for `%s`:" % filename
    labels = [version_parsing(v)[0] for v in unzip(alternatives)[1]]
    (name, version) = input_choice(labels, alternatives)
  else:
    (name, version) = alternatives[0]

  
  alternatives = list(reversed(group_to_name_alternatives(name)))
  if not alternatives:
    print "Incorrect name format: `%s`. Skipping" % filename
    return
  if len(alternatives) > 1:
    print "Choose a correct artifactId for `%s`:" % name
    labels = [name_parsing(a)[0] for a in unzip(alternatives)[1]]
    (group, name) = input_choice(labels, alternatives)
  else:
    (group, name) = alternatives[0]


  version, snapshot, source = version_parsing(version)
  name, source1 = name_parsing(name)

  return {
    "group": group,
    "name": name,
    "version": version,
    "snapshot": snapshot,
    "source": source or source1
  }



from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--interactive", 
                  dest="interactive", action="store_true", default=False,
                  help="Interactively resolve ambiguous names. Use this option to install libraries of different naming standards")
parser.add_option("-d", "--delete", 
                  dest="delete", action="store_true", default=False, 
                  help="Delete successfully installed libs in source location")
(options, args) = parser.parse_args()


parsings = (
  [(path, parse_interactively(path)) for path in jars("lib")]
  if options.interactive else
  [(path, parse_by_eclipse_standard(path)) for path in jars("lib")]
)

unparsable_files = [r[0] for r in parsings if r[1] == None]
if unparsable_files:
  print "The following files could not be parsed:"
  for f in unparsable_files:
    print "| - " + f


parsings = [p for p in parsings if p[1] != None]

for (path, parsing) in parsings:
  install(path, parsing)
  if options.delete:
    os.remove(path)

print maven_dependencies(parsings)
