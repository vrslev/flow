set -e
set -x

CUR_DIR="$(pwd)"
TEMP_DIR=/tmp/flow
ARCHIVE_NAME="$CUR_DIR/$(poetry version -s).zip"

rm -rf $TEMP_DIR
git clone . $TEMP_DIR
cd $TEMP_DIR
poetry export -o requirements.txt --without-hashes

zip -r $ARCHIVE_NAME requirements.txt flow
