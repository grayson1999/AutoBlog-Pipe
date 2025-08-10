.PHONY: setup run-once run-seed cron-install check clean help

# Default Python command (use python3 if available, otherwise python)
PYTHON := $(shell command -v python3 2> /dev/null || echo python)
PIP := $(shell command -v pip3 2> /dev/null || echo pip)

help:
	@echo "AutoBlog-Pipe Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  setup       - Install dependencies from requirements.txt"
	@echo "  run-once    - Generate and publish one batch of posts"
	@echo "  run-seed    - Generate initial 5-10 posts for seeding"
	@echo "  cron-install- Install cron job for daily publishing"
	@echo "  check       - Verify installation and imports"
	@echo "  clean       - Remove __pycache__ and temporary files"
	@echo "  help        - Show this help message"

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

cron-install:
	@echo "Installing cron job for daily posting..."
	@echo "Adding cron job: 0 9 * * * cd $(PWD) && make run-once"
	@(crontab -l 2>/dev/null; echo "0 9 * * * cd $(PWD) && make run-once") | crontab -
	@echo "Cron job installed successfully!"

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