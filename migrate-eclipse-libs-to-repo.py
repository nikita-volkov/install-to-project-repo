#!/usr/bin/python

# This is a utility script that moves all the eclipse libs in the lib/ folder to
# local repository and prints out Maven dependencies


import os
import re
import sets 
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

      return (group, name, version, source)
  return [(f, jarname_parsing(f)) for f in jars()]


def check_results(parsing_results):
  unparsable_files = [r[0] for r in parsing_results if r[1] == None]
  if unparsable_files:
    raise Exception("Unparsable file names detected: " + unparsable_files)


def maven_dependencies(parsing_results):
  def maven_dependency(group, name, version):
    return """
<dependency>
  <groupId>%s</groupId>
  <artifactId>%s</artifactId>
  <version>%s</version>
</dependency>
""" % (group, name, version)

  ids = [(group, name, version) for (file, (group, name, version, source)) in parsing_results]
  ids = sets.Set(ids)
  return "\n".join([maven_dependency(g, n, v).strip() for (g, n, v) in ids])


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
  def repo_path(group, name, version, source):
    return "repo/" \
         + "/".join(group.split(".")) \
         + "/" + name + "/" + version + "/" + name + "-" + version \
         + ("-sources" if source else "") \
         + ".jar"

  for (f, (g, n, v, s)) in parsing_results:
    move_file( "lib/" + f, repo_path(g, n, v, s) )
  
  
parsing_results = parsing_results()
check_results(parsing_results)
assort_files(parsing_results)
print maven_dependencies(parsing_results)
