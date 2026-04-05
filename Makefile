include .env
export

up:
	docker compose up -d

down:
	docker compose down

reset:
	docker compose down -v
	docker compose up -d

db-shell:
	docker exec -it pulse-db psql -U $(DB_USER) -d $(DB_NAME)

status:
	docker ps --filter "name=pulse"

logs:
	docker compose logs -f
