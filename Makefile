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
