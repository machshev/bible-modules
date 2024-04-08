.PHONY: all

all: md html

md: output/md/hebrew.md output/md/syriac.md

html: output/html/hebrew output/html/syriac

%.md:
	abm-tools gen bible -f md -a $(shell basename $*) $(shell basename $*) $(shell dirname $*)

output/html/%:
	abm-tools gen bible -f html -a $* $* $(shell dirname $@)

clean:
	rm -frv ./output
