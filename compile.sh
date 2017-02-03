#!/usr/bin/env bash

rm ./booking/templates/booking/agreement.odt
cd odt
zip -r ../booking/templates/booking/agreement.odt *
cd ..

