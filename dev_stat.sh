rep=origind

res=`git fetch $rep 2>&1; echo $?`

echo  "$res"
