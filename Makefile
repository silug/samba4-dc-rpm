# Makefile for source rpm: samba
# $Id$
NAME := samba
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
