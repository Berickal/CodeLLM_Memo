#!/bin/bash
# This script must be run after installing Defects4J. Paste this file inside the folder and then run it.

output_dir="defects4j_bugs_full"
mkdir -p $output_dir

project="Chart"
bug_id=1

for project in Chart Cli Closure Codec Compress Csv Gson JacksonCore JacksonDatabing JacksonXml Jsoup JxPath Lang Math Mockito Time; do
    for bug_id in $(seq 11 100); do
        echo "Processing $project-$bug_id"
        bug_dir="$output_dir/${project}_${bug_id}"
        mkdir -p "$bug_dir/buggy" "$bug_dir/fixed" "$bug_dir/tests"

        work_dir="defects4j_work"
        mkdir -p $work_dir
        cd $work_dir

        defects4j checkout -p $project -v ${bug_id}b -w buggy
        defects4j checkout -p $project -v ${bug_id}f -w fixed

        cd buggy
        buggy_classes=$(defects4j export -p classes.modified)
        test_classes=$(defects4j export -p tests.trigger)
        src_root=$(defects4j export -p dir.src.classes)
        test_root=$(defects4j export -p dir.src.tests)

        echo "project: $project" > "../../$bug_dir/metadata.txt"
        echo "bug_id: $bug_id" >> "../../$bug_dir/metadata.txt"
        echo "modified_classes: $buggy_classes" >> "../../$bug_dir/metadata.txt"
        echo "trigger_tests: $test_classes" >> "../../$bug_dir/metadata.txt"

        for class_name in $buggy_classes; do
            file_path=$(echo $class_name | tr '.' '/')
            cp "$src_root/$file_path.java" "../../$bug_dir/buggy/"
            cp "../fixed/$src_root/$file_path.java" "../../$bug_dir/fixed/"
        done

        for test_name in $test_classes; do
            file_path=$(echo $test_name | tr '.' '/')
            cp "$test_root/$file_path.java" "../../$bug_dir/tests/"
        done

        cd ../..
        echo "Export complete: $output_dir"
    done
done
