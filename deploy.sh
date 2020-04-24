#!/bin/bash

export userbin=~/bin

chmod 755 *.py

for f in *.py
do
  fullfile="$(pwd)/$f"
  filename="$(basename -- $f)"
  fname="${filename%.*}"
  fext="${filename##*.}"
  ln -s $fullfile $userbin/$fname
  chmod 755 $userbin/$fname
done

