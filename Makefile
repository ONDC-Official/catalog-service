.PHONY: setup run clean

# Environment variables
export ENV=dev

# Install make and python3
install:
	sudo apt install make
	sudo apt-get install python3-venv

# Set up the virtual environment and install dependencies
setup:
	python3 -m venv cron-venv
	. cron-venv/bin/activate && pip install elasticsearch

# Run the Python script
run:
	. cron-venv/bin/activate && python -m crons.delete_stale_data

# Clean up the environment
clean:
	rm -rf cron-venv

apply-es-mapping:
	@echo "Updating Elasticsearch mapping..."
	@if [ -z "$(index_name)" ]; then \
		read -p "Enter Elasticsearch index name: " index_name; \
	fi; \
	if [ -z "$(file_location)" ]; then \
		read -p "Enter path to the mapping file (JSON): " file_location; \
	fi; \
	curl -X PUT "http://localhost:9200/$$index_name/_mapping" -H "Content-Type: application/json" -d @$$file_location; \
	echo "Mapping update completed for index $$index_name."# take input of index name, json file location and hit localhost:9200
