classes=src/Commons.class
classes+=src/commons/ErrorPopup.class
classes+=src/commons/About.class
classes+=src/main/center/MainOptions.class
classes+=src/main/MainMenu.class
classes+=src/main/MainCenter.class
classes+=src/main/MainOperations.class
classes+=src/main/center/MainFiles.class
classes+=src/subprocess/RunXtermWMusync.class
classes+=src/MainFrame.class
classes+=src/MusyncSwing.class
classes+=src/SubProcess.class
classes+=src/SPWriter.class
classes+=src/MusyncSwing.class
classes+=src/commons/ModificationFrame.class
classes+=src/subprocess/ExportMusync.class

CP=src:src/main:src/main/center:src/subprocess:src/commons

include config.mk

all: $(classes)

build/musync-swing.jar:
	cd build && make
build/gfx:
	cp -R src/gfx/ build/gfx
build/MusyncSwing.class:
	cp $(classes) build

build: $(classes) build/MusyncSwing.class build/gfx build/musync-swing.jar
	$(RM) build/*.class

install: build
	cp build/musync-swing.jar $(prefix)/musync-swing.jar
	m4 -DPREFIX=$(prefix) scripts/musync-swing > $(prefix)/musync-swing
	chmod +x $(prefix)/musync-swing

uninstall:
	rm $(prefix)/musync-swing.jar
	rm $(prefix)/musync-swing

clean:
	$(RM) $(classes)
	$(RM) build/*.class
	$(RM) build/musync-swing.jar
	rm -Rf build/gfx

test: $(classes)
	${JAVA} -cp $(CP) MusyncSwing
