.PHONY: help pull-deploy push-deploy makemigrations migrate runserver createsuperuser collectstatic test install-nginx uninstall-nginx install-gunicorn uninstall-gunicorn

# Makefile

help:			
	@echo "==================================="
	@echo "  Django Project Makefile Commands "
	@echo "==================================="
	@awk -F':|##' ' \
		/^## / { \
			heading=substr($$0,4); \
			printf "\n\033[1;32m%s\033[0m\n", heading; \
		} \
		/^[a-zA-Z0-9_.-]+:.*##/ { \
			sub(/^[ \t]+/, "", $$1); \
			sub(/[ \t]+$$/, "", $$1); \
			sub(/^[ \t]+/, "", $$3); \
			sub(/[ \t]+$$/, "", $$3); \
			printf "  \033[36m%-20s\033[0m %s\n", $$1, $$3; \
		} \
	' $(MAKEFILE_LIST)

# Define a guard function to check for DEBUG mode
_debug_wrap:
	@if [ "$(DEBUG)" != "True" ]; then \
		echo "Error: This operation is only allowed in DEBUG mode. Set DEBUG=1 to proceed."; \
		exit 1; \
	fi


## Django Commands
makemigrations: ## Make migrations
	python manage.py makemigrations

migrate: makemigrations ## Apply migrations
	python manage.py migrate

runserver: migrate  ## Run the Django development server
	python manage.py runserver 0.0.0.0:8000

superuser: ## Create a superuser
	@python manage.py createsuperuser --no-input

collectstatic: ## Collect static files
	python manage.py collectstatic --noinput

test: ## Run tests
	pytest

flush: _debug_wrap ## Flush the database (delete all data!) 
	@if [ -z "$(DEBUG)" ]; then python manage.py flush; else python manage.py flush --noinput; fi
  


## Postgres Commands
install-db: ## Install Postgres
	./scripts/install_db.sh

create-db: ## Create the database
	python ./scripts/create_db.py > ./scripts/createdb.sql
	sudo -u postgres psql < ./scripts/createdb.sql
	@rm ./scripts/createdb.sql 

remove-db: _debug_wrap ## Remove the database
	python scripts/remove_db.py > ./scripts/dropdb.sql
	sudo -u postgres psql < ./scripts/dropdb.sql
	rm ./scripts/dropdb.sql # it contains sensitive information!


uninstall-rm-server: ## Uninstall rm-server
	./scripts/uninstall_rm-server.sh

uninstall-db: _debug_wrap ## Uninstall Postgres
	./scripts/uninstall_db.sh



clean:		## Remove pycache, tmp files and test db, mail, etc
	find . -name "*.pyc" -delete
	-find $(CURDIR) -type d -path "*__pycache__*" -not -path "*/.venv/*" -exec rm -rf {} \; #> /dev/null 2>&1
	./manage.py drop_test_database --noinput

schema:                 ## Use DRF Spectacular to generate schema for codegen to a python client
	python manage.py spectacular --api-version v1 --file schema.yaml


journal: ## View all relevant logs
	journalctl -f -n 50 -u gunicorn -u rm-queue -u rm-server -u nginx


rm-migrations: _debug_wrap ## Delete all migrations
	@read -p "Delete ALL migrations? [y/N] " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		exit 1; \
	fi
	rm **/migrations/0*.py
	rm */*/migrations/0*.py
	echo Deleted all migrations. Run 'make migrate' to recreate them.
