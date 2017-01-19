

export UBENCH_DEV='TRUE'
export UBENCH_PATH=$PWD

export UBENCH_CSS_PATH=${UBENCH_PATH}/css/asciidoctor-bench-report.css
export UBENCH_TEMPLATES_PATH=${UBENCH_PATH}/templates

export UBENCH_PLUGIN_DIR=${UBENCH_PATH}/ubench/plugins
export UBENCH_PLATFORM_DIR=${UBENCH_PATH}/platform
export UBENCH_CONF_DIR=${UBENCH_PATH}/conf
export UBENCH_BENCHMARK_DIR=${UBENCH_PATH}/benchmarks

function pathadd() {
    if [ -d "$1" ] && [[ ":$PATH:" != *":$1:"* ]]; then
	PATH="$1${PATH:+":$PATH"}"
    fi
}


pathadd ${UBENCH_PATH}/bin

if [[ $(hostname -s) = casanova* ]]; then
    source /opt/intel/2013.4/bin/compilervars.sh intel64
    function module() {
    echo "Empty module command"
    }

    export -f module
fi

if [ -e /usr/share/modules/init/bash ]; then
    source /usr/share/modules/init/bash
fi

