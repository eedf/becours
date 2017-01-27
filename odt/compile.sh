#!/usr/bin/env bash

rm ../booking/templates/booking/agreement.odt
zip ../booking/templates/booking/agreement.odt mimetype META-INF/manifest.xml content.xml meta.xml settings.xml styles.xml logo.png signature.png

