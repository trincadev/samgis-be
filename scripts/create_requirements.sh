#!/usr/bin/env bash

SCRIPT=$(realpath "$0")
SCRIPT_FOLDER=$(dirname "$SCRIPT")
ROOT_FOLDER=${SCRIPT_FOLDER}/../

mkdir -p tmp
rm ./tmp/requirements_tmp.txt || echo "./tmp/requirements_tmp.txt not found!"

echo "start requirements.txt preparation: pip freeze..."
pip freeze > ./tmp/freeze.txt
echo "grep python dependencies into freeze.txt..."
for x in $(cat ./requirements_no_versions.txt); do
  echo "# $x #"
  grep $x ./tmp/freeze.txt >> ./tmp/requirements_tmp.txt
  echo "######"
done

echo "cat ${ROOT_FOLDER}/tmp/requirements_tmp.txt"
cat ${ROOT_FOLDER}/tmp/requirements_tmp.txt
echo -e "\n"

[[ "$(echo -n 'Promote && sort "${ROOT_FOLDER}/tmp/requirements_tmp.txt" as new requirements.txt? [y/N]> ' >&2; read; echo $REPLY)" == [Yy]* ]] \
  && echo "copy requirements_tmp.txt to root project..." \
  || exit 0

sort ${ROOT_FOLDER}/tmp/requirements_tmp.txt > ${ROOT_FOLDER}/requirements.txt

echo "Fix any discrepancy within the new requirements.txt, bye!"

exit 0
