# Terminal-Bench 3.0 Task Factory — Makefile
# Author: Ambiguity Labs

TASK ?=
SCRIPTS = scripts

.PHONY: help create oracle nop pathcheck lint validate package list clean

help: ## Show this help
	@echo "Terminal-Bench 3.0 Task Factory"
	@echo "================================"
	@echo ""
	@echo "Usage: make <target> TASK=<task-name>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""

create: ## Scaffold a new task
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	@bash $(SCRIPTS)/create_task.sh $(TASK)

oracle: ## Run oracle solution and verify tests pass (reward=1)
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	uv run harbor run --agent oracle --path tasks/$(TASK)

nop: ## Verify tests FAIL without any solution (reward=0)
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	uv run harbor run --agent nop --path tasks/$(TASK)

pathcheck: ## Check for hardcoded host-machine paths
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	@bash $(SCRIPTS)/check_absolute_paths.sh $(TASK)

lint: ## Run ruff linter on Python files
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	@bash $(SCRIPTS)/lint.sh $(TASK)

validate: ## Run full validation pipeline (oracle + nop + pathcheck + lint)
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	@echo "=========================================="
	@echo "  Full Validation: $(TASK)"
	@echo "=========================================="
	@echo ""
	@bash $(SCRIPTS)/check_absolute_paths.sh $(TASK) && echo "" || exit 1
	@bash $(SCRIPTS)/lint.sh $(TASK) && echo "" || exit 1
	@bash $(SCRIPTS)/run_oracle.sh $(TASK) && echo "" || exit 1
	@bash $(SCRIPTS)/run_nop.sh $(TASK) && echo "" || exit 1
	@echo ""
	@echo "=========================================="
	@echo "  ALL CHECKS PASSED: $(TASK)"
	@echo "=========================================="

package: ## Create .zip for submission
	@test -n "$(TASK)" || (echo "ERROR: specify TASK=<name>" && exit 1)
	@bash $(SCRIPTS)/package_task.sh $(TASK)

list: ## List all tasks in development
	@echo "Tasks in development:"
	@ls -d tasks/*/ 2>/dev/null | sed 's|tasks/||;s|/||' | while read t; do \
		echo "  - $$t"; \
	done || echo "  (none)"
	@echo ""
	@echo "Packaged tasks:"
	@ls ready_to_submit/*.zip 2>/dev/null | sed 's|ready_to_submit/||;s|\.zip||' | while read t; do \
		echo "  - $$t"; \
	done || echo "  (none)"

clean: ## Remove Docker images for tasks
	@docker images --format '{{.Repository}}' | grep '^tb3-' | xargs -r docker rmi -f
	@echo "Cleaned up tb3-* Docker images"
