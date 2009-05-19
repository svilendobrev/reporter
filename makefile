#$Id$

now:
	$(MAKE) -C test

txt:
	python ./test/viewer.py
#	ln -s test/*txt .

# vim:ts=4:sw=4:noexpandtab
