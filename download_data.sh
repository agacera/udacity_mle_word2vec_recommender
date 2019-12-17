#!/bin/bash
mkdir data

if [[ "$1" == "full" ]]; then
    zip_file="ml-latest"
    link="http://files.grouplens.org/datasets/movielens/ml-latest.zip"
else
    zip_file="ml-latest-small"
    link="http://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
fi

cd data

echo "Downloading $link"

rm -rf "$zip_file".zip "$zip_file"
curl $link -o "$zip_file".zip 
unzip "$zip_file".zip 
rm "$zip_file".zip
