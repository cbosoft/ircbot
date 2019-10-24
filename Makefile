INSTALLED=/usr/bin/ircbot
SERVICE_DIR=/usr/lib/systemd/user
SERVICE=ircbot.service
SOURCE=ircbot.py


install:
	cp ${SOURCE} ${INSTALLED}
	mkdir -p ${SERVICE_DIR}
	cp ${SERVICE} ${SERVICE_DIR}/.

uninstall:
	rm ${INSTALLED}
	rm ${SERVICE_DIR}/${SERVICE}
