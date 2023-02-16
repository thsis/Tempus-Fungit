# If the first argument is "run"...
ifeq (recipe,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "run"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

prog: # ...
    # ...

.PHONY: recipe

recipe:
	python scripts/make_recipe.py $(RUN_ARGS)

install:
	scripts/install.sh

clean:
	scripts/clean.sh

export:
	scripts/export.sh
