
# Tells aclocal to put 'aclocal.m4' into the 'm4' directory
ACLOCAL_AMFLAGS = -I m4 ${ACLOCAL_FLAGS}

# Blank man target (used in doc)
man: 
	cd doc && $(MAKE) $(AM_MAKEFLAGS) man
.PHONY: man
	
# ADDITIONAL FILES TO INSTALL
EXTRA_DIST = \
	README.md \
	COPYING \
	AUTHORS \
	NEWS

# FILES NOT TO INSTALL
dist_noinst_SCRIPTS = autogen.sh antigen.sh
		    
# Config files
configdir = $(datadir)/portcullis
dist_config_DATA = \
		    data/default_filter.json \
		    data/selftrain_initial_neg.layer1.json \
		    data/selftrain_initial_neg.layer2.json \
		    data/selftrain_initial_neg.layer3.json \
		    data/selftrain_initial_neg.layer4.json \
		    data/selftrain_initial_neg.layer5.json \
		    data/selftrain_initial_neg.layer6.json \
		    data/selftrain_initial_neg.layer7.json \
		    data/selftrain_initial_pos.layer1.json \
		    data/selftrain_initial_pos.layer2.json \
		    data/selftrain_initial_pos.layer3.json

# SRC DIRS
make_dirs=deps/htslib-1.3 deps/ranger-0.3.8 lib src tests

if MAKE_JUNCTOOLS
    make_dirs += scripts
endif

if MAKE_DOCS
    make_dirs += doc
endif

SUBDIRS = $(make_dirs)
