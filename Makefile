ENV := .env
SUBDIRS := backend frontend
TARGETS := setup check test coverage

-include $(ENV)

.PHONY: $(TARGETS) $(SUBDIRS)
$(TARGETS): $(SUBDIRS)
$(SUBDIRS):
	@$(MAKE) -C $@ $(MAKECMDGOALS)

ssl-example/dhparams.pem:
	@mkdir -p $(dir $@)
	@openssl dhparam -out $@ 2048

ssl-example/cert.pem ssl-example/key.pem:
	@echo Generating snake-oil certificate: Running openssl
	@mkdir -p $(dir $@)
	@openssl req -x509 -newkey rsa:4096 -keyout $(dir $@)/key.pem -out $(dir $@)/cert.pem -days 365 -subj "/C=CA/ST=QC/L=Notre-Dame-du-Laus/O=mail/OU=mail/CN=${MAIL_HOSTNAME}" -sha256 -nodes

ssl/%.pem: ssl-example/%.pem
	@mkdir -p $(dir $@)
	@cp -d -n $^ $@

ssl: ssl/dhparams.pem ssl/cert.pem ssl/key.pem

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
