#$Id

_=
SPC=$_ $_
%.test: %.py
	@echo ===============
	PYTHONPATH=../..:$(PYTHONPATH) python $<

now: test.test

clean:
	rm *pyc

all: $(patsubst %.py,%.test,$(wildcard *.py))

# vim:ts=4:sw=4:noexpandtab
