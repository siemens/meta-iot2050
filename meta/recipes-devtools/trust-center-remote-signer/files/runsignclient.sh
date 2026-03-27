#!/bin/bash

set -e

SPOOLDIR=/var/spool/trust-center-remote-signer

rm -f $SPOOLDIR/out/hash

# set required env, such as TC_HOST, TC_PORT, TC_WORKER ...
# shellcheck source=/dev/null
source /usr/share/trust-center-credential/worker.env

echo Sign with trust center PPKI worker: $TC_HOST:$TC_PORT:$TC_WORKER

/usr/share/trust-center-remote-signer/sign-client/bin/signclient \
	signdocument \
	-signrequest -workerid $TC_WORKER \
	-indir $SPOOLDIR/in \
	-outdir $SPOOLDIR/out \
	-host $TC_HOST -port $TC_PORT \
	-keystore /usr/share/trust-center-credential/keystore \
	-keystorepwd $TC_KEYSTORE_PASSWD \
	-truststore /usr/share/trust-center-credential/truststore \
	-truststorepwd $TC_TRUSTSTORE_PASSWD \
	-metadata CLIENTSIDE_HASHDIGESTALGORITHM=SHA-512 \
	-metadata USING_CLIENTSUPPLIED_HASH=true
