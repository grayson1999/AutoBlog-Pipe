.PHONY: setup run-once run-seed run-dynamic cron-install cron-list cron-remove check clean test-logger help

# Default Python command (use python3 if available, otherwise python)
PYTHON := $(shell command -v python3 2> /dev/null || echo python)
PIP := $(shell command -v pip3 2> /dev/null || echo pip)

help:
	@echo "AutoBlog-Pipe Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup        - Install dependencies from requirements.txt"
	@echo "  run-once     - Generate and publish one batch of posts (topics.yml)"
	@echo "  run-seed     - Generate initial 5-10 posts for seeding (topics.yml)"
	@echo "  run-dynamic  - Generate post using dynamic pipeline (RSS+Research)"
	@echo "  cron-install - Install scheduled job for daily publishing"
	@echo "  cron-list    - List current AutoBlog scheduled jobs"
	@echo "  cron-remove  - Remove all AutoBlog scheduled jobs"
	@echo "  test-logger  - Test logging system"
	@echo "  check        - Verify installation and imports"
	@echo "  clean        - Remove __pycache__ and temporary files"
	@echo "  help         - Show this help message"

setup:
	@echo "Installing dependencies..."
	$(PIP) install -r requirements.txt
	@echo "Dependencies installed successfully!"

run-once:
	@echo "Running single post generation..."
	$(PYTHON) app/main.py --mode once

run-seed:
	@echo "Running initial seed generation (5-10 posts)..."
	$(PYTHON) app/main.py --mode seed

run-dynamic:
	@echo "Running dynamic content generation (RSS+Research)..."
	$(PYTHON) app/main.py --mode dynamic

cron-install:
	@echo "Installing scheduled job for daily publishing..."
	$(PYTHON) scripts/cron_setup.py install --schedule daily

cron-list:
	@echo "Listing AutoBlog scheduled jobs..."
	$(PYTHON) scripts/cron_setup.py list

cron-remove:
	@echo "Removing all AutoBlog scheduled jobs..."
	$(PYTHON) scripts/cron_setup.py remove

test-logger:
	@echo "Testing logging system..."
	$(PYTHON) app/utils/logger.py

check:
	@echo "Checking Python and dependencies..."
	@$(PYTHON) --version
	@echo "Testing imports..."
	@$(PYTHON) -c "import openai; print('✓ openai')"
	@$(PYTHON) -c "import yaml; print('✓ yaml')"
	@$(PYTHON) -c "import jinja2; print('✓ jinja2')"
	@$(PYTHON) -c "import git; print('✓ GitPython')"
	@$(PYTHON) -c "import markdown; print('✓ markdown')"
	@$(PYTHON) -c "import unidecode; print('✓ unidecode')"
	@$(PYTHON) -c "import dotenv; print('✓ python-dotenv')"
	@echo "All dependencies OK!"

clean:
	@echo "Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean completed!"