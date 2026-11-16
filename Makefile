.PHONY: dev migrate test
dev:
	./run.sh
migrate:
	python3 -c 'from src.database import open_database; open_database().dispose()'
test:
	./test.sh
