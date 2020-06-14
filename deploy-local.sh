#!/bin/sh
docker build -t ccd . && docker stop ccd && docker rm ccd && docker run -d -e VIRTUAL_HOST=citycouncil.blackmad.com --name=citycouncil ccd