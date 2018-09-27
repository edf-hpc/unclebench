

export UBENCH_DEV='TRUE'
export UBENCH_PATH=$PWD

export UBENCH_CSS_PATH=${UBENCH_PATH}/css/asciidoctor-bench-report.css
export UBENCH_TEMPLATES_PATH=${UBENCH_PATH}/templates

export UBENCH_PLUGIN_DIR=${UBENCH_PATH}/ubench/plugins
export UBENCH_PLATFORM_DIR=${UBENCH_PATH}/platform
export UBENCH_CONF_DIR=${UBENCH_PATH}/conf
export UBENCH_BENCHMARK_DIR=${UBENCH_PATH}/benchmarks


export PYTHONPATH=$PYTHONPATH:${UBENCH_PATH}
function pathadd() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
	PATH="$1${PATH:+":$PATH"}"
    fi
}


pathadd ${UBENCH_PATH}/bin

if [ -e /usr/share/modules/init/bash ]; then
    source /usr/share/modules/init/bash
fi

# creating temporal directories

if [[ ! -z "$UBENCH_DIR_CREATE" ]]; then

    mkdir -p /tmp/ubench_run_dir
    mkdir -p /tmp/ubench_resource_dir
    export UBENCH_RUN_DIR_BENCH=/tmp/ubench_run_dir
    export UBENCH_RESOURCE_DIR=/tmp/ubench_resource_dir
fi
