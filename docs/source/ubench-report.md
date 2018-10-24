% ubench-report(1)

# NAME


ubench-report - Build a performance report

# SYNOPSIS

    ubench report -m <metadata_file> -o <output_dir>

    ubench report -h

# DESCRIPTION


*ubench report*   Build a performance report from information set in metadata_file.
		  Report files are written un output_dir.

# OPTIONS

# -m, --metadata-file <metadata_file>
  Yaml file defining data that should be written in the report.
  You can find an example below. Dates must be in "AAAA-MM-DD HH:MM:SS" format. 

```
author: '<Report author>'
sessions:
    - default:
        platform: '<platform_name>'
    - '<session1_name>':
        tester: '<session1_tester_name>'
       	dir:<session1_result_directory>
        date_start: <start_date_session1>
        date_end: <end_date_session1>
    - '<session2_name>':
        tester: '<session2_tester_name>'
        dir:<session2_result_directory>
        date_start: <start_date_session2>
        date_end: <end_date_session2>
    - ...

contexts:
    - default:
        compare: True
	compare_threshold: '5'
        context:
            - 'nodes'
            - 'tasks'
        context_res: 'mpi_version'
    - '<bench1_name>':
        compare_threshold: '1'
        context:
            - 'nodes'
        context_res: 'mpi_version'
    - ...

benchmarks:
    - default:
        result: 'ok'
    - '<bench1_name>':
        '<session1_name>':
            comment: '<bench1_name_s1_comment>'
        '<session2_name>':
            comment: '<bench1_name_s1_comment>'
    - '<bench2_name>':
        '<session1_name>':
            comment: '<bench2_name_s2_comment>'
        '<session2_name>':
            comment: '<bench2_name_s2_comment>'
    - ...
```


# -r, --results-directory <results_directory>
  Directory where peformances results are extracted.

# -o, --output-dir <output_directory>
  Output directory where report files are written.


# ENVIRONMENT

## UBENCH_TEMPLATES_PATH
   **default :** /usr/share/unclebench/templates
   Path from where Jinja2 template files are loaded.

## UBENCH_CSS_PATH
   **default :** /usr/share/unclebench/css/asciidoctor-bench-report.css
   Path to the CSS style sheet used to render the report in HTML format.



ubench-fetch(1), ubench-run(1), ubench-list(1), ubench-log(1), ubench-result(1), ubench-listparams(1)
