install:
	scripts/install.sh

clean:
	scripts/clean.sh

export:
	scripts/export.sh

recipe RECIPE:
	python scripts/make_recipe.py $(RECIPE)
