prefix=/usr/local/bin

# change this if your program doesn't compile
JAVAC=javac
JOPTS=-Xlint:deprecation
JAVA=java

.SUFFIXES: .java .class

.java.class:
	$(JAVAC) -cp $(CP) $(JOPTS) $*.java
