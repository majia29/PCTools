
export userbin=~/bin

chmod 755 *.py

for f in *.py
do
  filename="$(basename -- $f)"
  fname="${filename%.*}"
  fext="${filename##*.}"
  ln -s $f $userbin/$fname
  chmod 755 $userbin/$fname
done

