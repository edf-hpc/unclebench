% ubench-report(1)

# NAME


ubench-report -  Build a performance report

# SYNOPSIS


    ubench report -p <platform> -b <bench> [<bench> ...]

    ubench report -h

# DESCRIPTION


*ubench report*   Build a performance report,  given a platform and a list of benchmarks.
              Avaible benchmarks runs can be found using *ubench list* command.

# OPTIONS

# -p <platform>
  Name of the platform where benchmarks were run.


# -b <bench> [<bench> ...]
  Names of the benchmarks whose report should be built


# ENVIRONMENT

## UBENCH_REPORT_DIR
   **default :** /scratch/<user>/Ubench/report
   Path where reports are built.
   
## UBENCH_RUN_DIR_BENCH
   **default :** /scratch/<user>/Ubench/benchmarks
   Path where benchmarks are looked for.
   
## UBENCH_TEMPLATES_PATH
   **default :** /usr/share/unclebench/templates
   Path from where Jinja2 template files are loaded.

## UBENCH_CSS_PATH
   **default :** /usr/share/unclebench/css/asciidoctor-bench-report.css
   Path to the CSS style sheet used to render the report in html format.


ubench-fetch(1), ubench-run(1), ubench-list(1), ubench-log(1), ubench-result(1), ubench-listparams(1)