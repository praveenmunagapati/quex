for x in `find -maxdepth 3 -mindepth 1 -type f -or -path "*.svn*" -prune -or -print`; do 
    pushd $x; 
    if [ -e Makefile -o -e makefile ]; then
        echo "clean: $x"; 
        make clean; 
        rm -f tmp.txt
        rm -f tmp[10].txt
    fi
    popd
done
