#!/usr/bin/python

# A script for installing jars to an in-project Maven repository. 
# 
# MIT License
# (c) 2012, Nikita Volkov. All rights reserved.
# http://github.com/nikita-volkov/install-to-local-repo
# 


import os
import re
import shutil


def parsing_results():
  def jars():
    return [f for f in os.listdir("./lib") if f.lower().endswith(".jar")]
  def jarname_parsing(file):
    match = re.match("([\w\.]+)_(\d+\.\d+\.\d+.*)\.jar", file)
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
  return [("lib/" + f, jarname_parsing(f)) for f in jars()]


def check_results(parsing_results):
  unparsable_files = [r[0] for r in parsing_results if r[1] == None]
  if unparsable_files:
    raise Exception("Unparsable file names detected: \r\n" \
                  + "\r\n".join(unparsable_files))

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


def move_file(src, dst):
  def create_tree(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
      os.makedirs(d)
  create_tree(dst)
  if os.path.exists(dst):
    os.remove(dst)
  shutil.move(src, dst)


def assort_files(parsing_results):

  def cmd((f, p)):
    return "install:install-file" \
         + " -Dfile=" + f \
         + " -DgroupId=" + p["group"] \
         + " -DartifactId=" + p["name"] \
         + " -Dversion=" + p["version"] + ("-SNAPSHOT" if p["snapshot"] else "") \
         + " -Dpackaging=jar" \
         + " -DlocalRepositoryPath=repo" \
         + " -DcreateChecksum=true" \
         + (" -Dclassifier=sources" if p["source"] else "")

  for r in parsing_results:
    os.system("mvn " + cmd(r))

  

parsing_results = parsing_results()
check_results(parsing_results)
assort_files(parsing_results)
print maven_dependencies(parsing_results)
