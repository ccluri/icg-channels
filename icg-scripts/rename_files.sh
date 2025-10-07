
# for i in */*.tau.dat; do
#     NEWNAME="${i/%.tau.dat/.tau.6_5.dat}"
#     echo "./$i" "./$NEWNAME"
#     #git status $i
#     ( git mv ./$i ./$NEWNAME )
# done

for i in */*.6_5.dat; do
    NEWNAME="${i/%.6_5.dat/.6_3.dat}"
    echo "./$i" "./$NEWNAME"
    #git status $i
    ( git mv ./$i ./$NEWNAME )
done


# for i in */*.37.dat; do
#     ( git add ./$i )
# done
