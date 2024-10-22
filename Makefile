# all: up

# up:
# 	@docker-compose up --build

# migrate:
# 	@python3 -m venv .venv && \
#     ( \
#         trap 'deactivate' EXIT; \
#         source .venv/bin/activate && \
#         pip install python-dotenv "psycopg[binary]" && \
#         python3 auth-service/src/database/apply_migration.py auth-service/src/database/migrations \
#     )

# down:
# 	@docker-compose down

# clean: down
# 	@docker images -q | xargs docker rmi
# 	@docker volume ls -q | xargs docker volume rm
# 	rm -rf .venv

# re: clean all

# fclean: clean
# 	@docker system prune -af