Name:		felix-gogo-runtime
Version:	1.2.0
Release:	1
Summary:	Apache Felix Gogo runtime
Group:		Development/Java
License:	ASL 2.0
URL:		https://felix.apache.org/
Source0:	https://repo1.maven.org/maven2/org/apache/felix/org.apache.felix.gogo.runtime/%{version}/org.apache.felix.gogo.runtime-%{version}-sources.jar

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.osgi:org.osgi.service.event)
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:org.osgi.namespace.service)
BuildRequires:	mvn(org.osgi:org.osgi.service.component.annotations)
BuildSystem:	maven
BuildOption(install):	--file-name org.apache.felix.gogo.runtime --link %{name}
Obsoletes:	%{name}-javadoc < %{version}-%{release}

%description
Apache Felix Gogo runtime 1.2.0. This jar contains the command shell
runtime, the command API, and the thread IO API. Framework types come
from OSGi Core 6. Command execution events are delivered through Event
Admin. Versioning, bundle, and component annotations are compile-time
only. This build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
cp -p META-INF/LICENSE LICENSE
cp -p META-INF/NOTICE NOTICE
rm -rf META-INF
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path

java_files = list(Path("src/main/java").rglob("*.java"))
if len(java_files) != 46:
    raise SystemExit("java files " + str(len(java_files)))
for name in (
    "src/main/java/org/apache/felix/gogo/runtime/CommandProcessorImpl.java",
    "src/main/java/org/apache/felix/service/command/CommandProcessor.java",
    "src/main/java/org/apache/felix/service/threadio/ThreadIO.java",
    "src/main/java/org/apache/felix/gogo/runtime/activator/EventAdminListener.java",
):
    if not Path(name).is_file():
        raise SystemExit("missing " + name)
license_text = Path("LICENSE").read_text(encoding="utf-8")
if "Apache License" not in license_text:
    raise SystemExit("LICENSE is not the Apache license")
if "Apache Felix Gogo Runtime" not in Path("NOTICE").read_text(encoding="utf-8"):
    raise SystemExit("NOTICE mismatch")
if list(Path(".").rglob("*.jar")) or list(Path(".").rglob("*.class")):
    raise SystemExit("prebuilt binary remains")
for pom in Path(".").rglob("pom.xml"):
    pom.unlink()

# gogo-parent 7 parents felix-parent 8, which cooker does not ship.
Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.apache.felix</groupId>
  <artifactId>org.apache.felix.gogo.runtime</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>Apache Felix Gogo Runtime</name>
  <description>Apache Felix Gogo command shell runtime.</description>
  <url>https://felix.apache.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.event</artifactId>
      <version>1.4.1</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.namespace.service</artifactId>
      <version>1.0.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.service.component.annotations</artifactId>
      <version>1.5.1</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
poms = sorted(str(path) for path in Path(".").rglob("pom.xml"))
if poms != ["pom.xml"]:
    raise SystemExit("poms " + str(poms))
for needle in (
    "<artifactId>org.apache.felix.gogo.runtime</artifactId>",
    "<artifactId>osgi.core</artifactId>",
    "<version>6.0.0</version>",
    "<artifactId>org.osgi.service.event</artifactId>",
    "<version>1.4.1</version>",
    "<artifactId>osgi.annotation</artifactId>",
    "<version>8.1.0</version>",
    "<artifactId>org.osgi.namespace.service</artifactId>",
    "<version>1.0.0</version>",
    "<artifactId>org.osgi.service.component.annotations</artifactId>",
    "<version>1.5.1</version>",
    "<scope>provided</scope>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "<packaging>jar</packaging>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("junit", "SNAPSHOT", "<source>", "<target>", "<parent>", "maven-bundle-plugin", "mockito"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.apache.felix.gogo.runtime-%{version}.jar --describe-module org.apache.felix.gogo.runtime > module-describe.txt
grep -q '^org.apache.felix.gogo.runtime' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc LICENSE NOTICE
