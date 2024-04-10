.PHONY: all

all: md vpl html osis

md: output/md/hebrew.md output/md/syriac.md

vpl: output/vpl/hebrew.vpl output/vpl/syriac.vpl

osis: output/osis/hebrew.osis output/osis/syriac.osis

html: output/html/hebrew output/html/syriac

%.md:
	abm-tools gen bible -f md -a $(shell basename $*) $(shell basename $*) $(shell dirname $*)

%.vpl:
	abm-tools gen bible -f vpl -a $(shell basename $*) $(shell basename $*) $(shell dirname $*)

%.osis:
	abm-tools gen bible -f osis -a $(shell basename $*) $(shell basename $*) $(shell dirname $*)

output/html/%:
	abm-tools gen bible -f html -a $* $* $(shell dirname $@)

clean:
	rm -frv ./output
