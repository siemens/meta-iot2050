EFIBOOTGUARD_NUM_CONFIG_PARTS ?= ""

# The non-swupdate example image uses a single BOOT partition, so allow efibootguard
# to be built with one expected config partition for that specific build only.
do_prepare_build:append() {
	if [ -n "${EFIBOOTGUARD_NUM_CONFIG_PARTS}" ] && \
	   ! grep -q '^override_dh_auto_configure:' ${S}/debian/rules; then
		sed -i '/^%:/i override_dh_auto_configure:\n\tdh_auto_configure -- --with-num-config-parts=${EFIBOOTGUARD_NUM_CONFIG_PARTS}\n' \
			${S}/debian/rules
	fi
}