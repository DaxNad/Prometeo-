
.PHONY: tl-eval goal-complete-v1
tl-eval:
	./scripts/run_tl_eval.sh

goal-complete-v1:
	bash scripts/goal_complete_v1_check.sh

.PHONY: product-complete-roadmap
product-complete-roadmap:
	bash scripts/product_complete_roadmap_check.sh

.PHONY: product-core-closure-v1
product-core-closure-v1:
	bash scripts/product_core_closure_v1_check.sh

.PHONY: controlled-import-pipeline-v1
controlled-import-pipeline-v1:
	bash scripts/controlled_import_pipeline_v1_check.sh

.PHONY: controlled-import-schema-contract-v1
controlled-import-schema-contract-v1:
	bash scripts/controlled_import_schema_contract_v1_check.sh
	PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -s backend/tests/test_controlled_import_schema_contract.py -q

.PHONY: controlled-import-no-apply-guard-v1
controlled-import-no-apply-guard-v1:
	bash scripts/controlled_import_no_apply_guard_v1_check.sh

.PHONY: controlled-import-apply-contract-v1
controlled-import-apply-contract-v1:
	bash scripts/controlled_import_apply_contract_v1_check.sh

.PHONY: controlled-import-persistent-audit-contract-v1
controlled-import-persistent-audit-contract-v1:
	bash scripts/controlled_import_persistent_audit_contract_v1_check.sh

.PHONY: controlled-import-audit-storage-decision-v1
controlled-import-audit-storage-decision-v1:
	bash scripts/controlled_import_audit_storage_decision_v1_check.sh

.PHONY: controlled-import-audit-db-schema-contract-v1
controlled-import-audit-db-schema-contract-v1:
	bash scripts/controlled_import_audit_db_schema_contract_v1_check.sh

.PHONY: controlled-import-audit-migration-v1
controlled-import-audit-migration-v1:
	bash scripts/controlled_import_audit_migration_v1_check.sh
