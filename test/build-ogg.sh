function create_bogus_ogg() {
    oggenc -a "$1" -l "$2" -t "$3" -N "$4" -r /dev/null -o "$5" &> /dev/null
}

BUILDDIR=./ogg_build

if ! which oggenc > /dev/null; then
    echo "sorry, you don't have oggenc"
    exit 1
fi

if [[ ! -d $BUILDDIR ]]; then
    mkdir $BUILDDIR
fi

source ref.sh

for a in $(seq 0 $[${#ARTISTS[*]} - 1]); do
    echo $BUILDDIR/${ARTISTS[$a]}
    for l in $(seq 0 $[${#ALBUMS[*]} - 1]); do
        track=1;
        for t in $(seq 0 $[${#TITLES[*]} - 1]); do
            create_bogus_ogg "${ARTISTS[$a]}" "${ALBUMS[$l]}" "${TITLES[$t]}" "$track" "$BUILDDIR/$track-${ARTISTS[$a]}-${ALBUMS[$l]}-${TITLES[$t]}.ogg"
            track=$[$track + 1]
        done
    done;
done;

echo "done building files in $BUILDDIR"
