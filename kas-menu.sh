#!/bin/sh

if ! pip3 show -q kconfiglib 2>/dev/null; then
	pip3 install --user kconfiglib
fi

${HOME}/.local/bin/menuconfig

source ./.config

for include in $(grep CONFIG_KAS_INCLUDE_ .config); do
	varname=${include%%=*}
	KAS_INCLUDES="${KAS_INCLUDES}${!varname}"
done

for var in $(grep CONFIG_KAS_VAR_ .config); do
	var_name=${var##*=\"}
	var_name=${var_name%%\"}
	var_value=CONFIG_${var##CONFIG_KAS_VAR_}
	var_value=${var_value%%=*}
	RUNTIME_ARGS="${RUNTIME_ARGS} -e ${var_name}=${!var_value}"
done

if [ -n "${RUNTIME_ARGS}" ]; then
	ENABLE_RUNTIME_ARGS="--runtime-args"
fi

echo "Running kas-container ${ENABLE_RUNTIME_ARGS} ${RUNTIME_ARGS} build ${CONFIG_KAS_MAIN}${KAS_INCLUDES}..."
kas-container ${ENABLE_RUNTIME_ARGS} "${RUNTIME_ARGS}" build ${CONFIG_KAS_MAIN}${KAS_INCLUDES}
