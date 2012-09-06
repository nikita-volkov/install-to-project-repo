#About
A Python script for easily installing libraries to an in-project Maven repository. It creates a repository in the root folder of the project complete with poms, checksums and metadata. It also outputs the appropriate dependencies xml to be inserted in your `pom` file.

#How it works
* It looks for jars having name of Eclipse standard, which has the following format: 

        groupId.artifactId[.source]_version[.SNAPSHOT].jar

* It ignores any files which are not jars.

* It exits with an error if the `lib` directory contains any jars of unsupported naming format, not performing any side effects.

* After successful installation of all jars it prints out all according dependencies for your `pom`.

#Using
Just run it from the folder containing your lib folder. 

After the script is complete copy-paste the generated dependencies xml to your `pom` under `dependencies` tag and add the following under the `repositories` tag:

    <repository>
      <id>project</id>
      <url>file://${project.basedir}/repo</url>
    </repository>

For more details and information about what to be aware of please read [this StackOverflow answer](http://stackoverflow.com/a/7623805/485115).

#Example
If the structure of the `lib` folder is as follows:

    lib/
    | - org.eclipse.e4.xwt_0.9.1.SNAPSHOT.jar
    | - org.eclipse.e4.xwt.source_0.9.1.SNAPSHOT.jar

It will result in the project's repository of the following structure having been created:
    
    repo/
    | - org/
    |   | - eclipse/
    |   |   | - e4/
    |   |   |   | - xwt/
    |   |   |   |   | - 0.9.1-SNAPSHOT/
    |   |   |   |   |   | - maven-metadata-local.xml
    |   |   |   |   |   | - maven-metadata-local.xml.md5
    |   |   |   |   |   | - maven-metadata-local.xml.sha1
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT-sources.jar
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT-sources.jar.md5
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT-sources.jar.sha1
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.jar
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.jar.md5
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.jar.sha1
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.pom
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.pom.md5
    |   |   |   |   |   | - xwt-0.9.1-SNAPSHOT.pom.sha1
    |   |   |   |   | - maven-metadata-local.xml
    |   |   |   |   | - maven-metadata-local.xml.md5
    |   |   |   |   | - maven-metadata-local.xml.sha1

It will also print out the Maven installation process log info messages followed by this Maven dependency to be inserted in your `pom`:

    <dependency>
      <groupId>org.eclipse.e4</groupId>
      <artifactId>xwt</artifactId>
      <version>0.9.1-SNAPSHOT</version>
    </dependency>
