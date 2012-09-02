# Makefile for gimp label templates script-fu

GIMPTOOL = gimptool-2.0

labels.scm: labeltemplates.scm labels.scm-dist
	cat labeltemplates.scm labels.scm-dist >labels.scm

install: labels.scm
	$(GIMPTOOL) --install-script labels.scm

labeltemplates.scm:
	if ! test -s labeltemplates.scm; then cp labeltemplates.scm-dist labeltemplates.scm; fi

templates:
	make-label-fu.py >labeltemplates.scm

clean:
	rm labels.scm

