
.PHONY: tl-eval goal-complete-v1
tl-eval:
	./scripts/run_tl_eval.sh

goal-complete-v1:
	bash scripts/goal_complete_v1_check.sh

.PHONY: product-complete-roadmap
product-complete-roadmap:
	bash scripts/product_complete_roadmap_check.sh

