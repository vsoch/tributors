#!/bin/bash

echo
echo "************** START: test_client.sh **********************"

# Create temporary testing directory
echo "Creating temporary directory to work in."
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

. $here/helpers.sh

# Create temporary testing directory
tmpdir=$(mktemp -d)
output=$(mktemp ${tmpdir:-/tmp}/rse_test.XXXXXX)
printf "Created temporary directory to work in. ${tmpdir}\n"

# Make sure it's installed
if which tributors >/dev/null; then
    printf "tributors is installed\n"
else
    printf "tributors is not installed\n"
    exit 1
fi

echo
echo "#### Testing init zenodo"
runTest 1 $output tributors init zenodo --zenodo-file $tmpdir/.zenodo.json
runTest 0 $output tributors init zenodo --zenodo-file $tmpdir/.zenodo.json --doi 10.5281/zenodo.1012531 --repo singularityhub/sregistry
runTest 1 $output tributors init zenodo --zenodo-file $tmpdir/.zenodo.json --doi 10.5281/zenodo.1012531 --repo singularityhub/sregistry

echo
echo "#### Testing init allcontrib"
runTest 0 $output tributors init allcontrib --allcontrib-file $tmpdir/.all-contributorsrc
runTest 1 $output tributors init allcontrib --allcontrib-file $tmpdir/.all-contributorsrc
runTest 0 $output tributors init allcontrib --allcontrib-file $tmpdir/.all-contributorsrc --force

echo
echo "#### Testing init with malformed name"
runTest 1 $output tributors init --allcontrib-file $tmpdir/.all-contributorsrc --repo pancakes-hub


echo "#### Testing update zenodo"
runTest 0 $output tributors update zenodo --zenodo-file $tmpdir/.zenodo.json

echo "#### Testing update allcontrib"
runTest 0 $output tributors update allcontrib --allcontrib-file $tmpdir/.all-contributorsrc

rm -rf ${tmpdir}
