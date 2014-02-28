include $(REP_DIR)/ports/exfat.inc
EXFAT_DIR = $(REP_DIR)/contrib/$(EXFAT)

TARGET   = exfat_fuse_fs

SRC_C  = $(notdir $(EXFAT_DIR)/fuse/main.c)
SRC_CC   = fuse_fs_main.cc \
           init.cc

LIBS     = base config server libc libc_log libc_block libfuse libexfat
INC_DIR += $(PRG_DIR)/..

CC_OPT += -Wno-unused-function

vpath %.c             $(EXFAT_DIR)/fuse
vpath fuse_fs_main.cc $(PRG_DIR)/..
vpath init.cc         $(PRG_DIR)/../../../lib/exfat