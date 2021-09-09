#!/bin/bash
shopt -s extglob
for FILTERFOLDER in *; do
	if [ -d "$FILTERFOLDER" ]; then
		echo "--->" $FILTERFOLDER;
	fi;
done;

