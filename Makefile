-include .env

SUBDIRS := backend
TARGETS := setup check test coverage

.PHONY: $(TARGETS) $(SUBDIRS)
$(TARGETS): $(SUBDIRS)
$(SUBDIRS):
	@$(MAKE) -C $@ $(MAKECMDGOALS)

ssl-example:
	@echo Generating snake-oil certificate: Running openssl
	@mkdir -p $@
	@openssl dhparam -out $@/dhparams.pem 2048
	@openssl req -x509 -newkey rsa:4096 -keyout $@/key.pem -out $@/cert.pem -days 365 -subj "/C=CA/ST=QC/L=Notre-Dame-du-Laus/O=mail/OU=mail/CN=${MAIL_HOSTNAME}" -sha256 -nodes

ssl: ssl-example
	@echo Copying snake-oil certificate
	@mkdir -p $@
	@cp -n -d $^/*.pem $@/

.PHONY: deploy
deploy: ssl
	@echo Deploying
	@docker compose pull
	@docker compose up --force-recreate --build -d
	@docker image prune -f

.PHONY: undeploy
undeploy:
	@echo Undeploying
	@docker compose down

.PHONY: clean
clean:
	@echo Cleaning ignored files
	@git clean -Xfd

.DEFAULT_GOAL := test
