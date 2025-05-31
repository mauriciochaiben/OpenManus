# ...existing content...

# Vector Database Commands
.PHONY: chromadb-up chromadb-down chromadb-reset chromadb-backup chromadb-restore

chromadb-up: ## Start ChromaDB service
	@echo "🚀 Starting ChromaDB..."
	docker-compose up -d chromadb
	@echo "⏳ Waiting for ChromaDB to be ready..."
	@until curl -f http://localhost:8001/api/v1/heartbeat > /dev/null 2>&1; do sleep 2; done
	@echo "✅ ChromaDB is ready!"
	@chmod +x scripts/init-chromadb.sh
	@./scripts/init-chromadb.sh

chromadb-down: ## Stop ChromaDB service
	@echo "🛑 Stopping ChromaDB..."
	docker-compose stop chromadb

chromadb-reset: ## Reset ChromaDB data (⚠️  WARNING: This will delete all data!)
	@echo "⚠️  WARNING: This will delete all ChromaDB data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		docker-compose down chromadb; \
		sudo rm -rf ./data/chromadb/*; \
		echo "✅ ChromaDB data reset complete!"; \
	else \
		echo ""; \
		echo "❌ Reset cancelled."; \
	fi

chromadb-backup: ## Backup ChromaDB data
	@echo "💾 Creating ChromaDB backup..."
	@mkdir -p ./backups
	@tar -czf "./backups/chromadb-backup-$$(date +%Y%m%d-%H%M%S).tar.gz" -C ./data chromadb
	@echo "✅ Backup created in ./backups/"

chromadb-restore: ## Restore ChromaDB from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Please specify BACKUP_FILE=<backup_file>"; \
		exit 1; \
	fi
	@echo "📥 Restoring ChromaDB from $(BACKUP_FILE)..."
	@docker-compose down chromadb
	@rm -rf ./data/chromadb/*
	@tar -xzf "$(BACKUP_FILE)" -C ./data/
	@echo "✅ Restore complete!"

# Update existing commands to include ChromaDB
dev-up: chromadb-up ## Start all development services including ChromaDB
	docker-compose up -d

dev-down: ## Stop all development services
	docker-compose down

dev-reset: chromadb-reset ## Reset all development data including ChromaDB
	@echo "⚠️  WARNING: This will reset ALL development data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo ""; \
		docker-compose down -v; \
		sudo rm -rf ./data/*; \
		echo "✅ All development data reset!"; \
	fi
