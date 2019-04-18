#!/bin/bash

../list_errors.sh | cut -f 7-8 -d' ' | while read l ; do ../generate_url.sh $l ; done
