import os
import argparse
import pandas as pd
from textwrap import dedent
from src.utilities import get_abs_path


template = dedent("""
    {TITLE}

    Ingredients
    - 

    Instructions
    """)


def create_recipe(name, outfile):
    print(f"Creating new Recipe: {name}")
    assert not os.path.exists(outfile), f"file {name}.txt exists already in 'recipes' directory."
    with open(outfile, "w") as f:
        # skip first character (newline)
        f.write(template[1:].format(TITLE=name))

    os.system(f"gedit {outfile}")


def validate_recipe(name, outfile):
    with open(outfile) as f:
        recipe = f.read()

    title = get_title(recipe)
    instructions = get_instructions(recipe)
    ingredients = get_ingredients(recipe)
    print(f"parsed title as: {title}")
    print(f"parsed ingredients as: {ingredients}")
    print(f"parsed instructions as: {instructions}")
    user_okay = input("proceed? [y/n]>:").lower() == "y"
    if user_okay:
        return name, title, ingredients, instructions
    else:
        os.system(f"gedit {outfile}")
        return validate_recipe(name, outfile)


def get_title(recipe):
    return recipe.splitlines()[0]


def get_instructions(recipe):
    lines = recipe.splitlines()
    start = lines.index("Instructions") + 1
    return "\n".join(lines[start:])


def get_ingredients(recipe):
    lines = recipe.splitlines()
    start = lines.index("Ingredients") + 1
    stop = lines.index("Instructions")
    return ";".join([line.replace("-", "").replace("*", "") for line in lines[start:stop] if line])


def construct_data_frame(name, title, instructions, ingredients):
    df = pd.DataFrame({"recipe_filename": name,
                       "recipe_title": title,
                       "ingredients_str": ingredients,
                       "instructions_str": instructions},
                      index=[pd.Timestamp.now()]).rename_axis(index="created_at")
    return df


def save_to_seeds_directory(df):
    seed_file = get_abs_path("data", "seeds", "recipes.csv")
    df.to_csv(seed_file, mode="a", header=not os.path.exists(seed_file))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("RECIPE", help="name of recipe to create.")
    args = parser.parse_args()
    OUTFILE = get_abs_path("recipes", f"{args.RECIPE}.txt")
    create_recipe(args.RECIPE, OUTFILE)
    NAME, TITLE, INGREDIENTS, INSTRUCTIONS = validate_recipe(args.RECIPE, OUTFILE)
    DF = construct_data_frame(name=NAME, title=TITLE, ingredients=INGREDIENTS, instructions=INSTRUCTIONS)
    save_to_seeds_directory(DF)

