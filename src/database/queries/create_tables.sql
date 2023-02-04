CREATE SCHEMA "experiments";

CREATE SCHEMA "sites";

CREATE SCHEMA "recipes";

CREATE TABLE "experiments"."dim_strains" (
  "strain_id" SERIAL PRIMARY KEY,
  "strain_name" text,
  "type" text,
  "source" text,
  "is_single_genetic" boolean,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "experiments"."dim_agar_plates" (
  "agar_plate_id" SERIAL PRIMARY KEY,
  "medium_id" int,
  "medium_amount" float,
  "mediium_unit" text,
  "starter_id" int,
  "starter_amount" float,
  "starter_unit" text,
  "disinfectant_id" int,
  "container_area_mm2" float,
  "container_height_mm" float,
  "container_type" text,
  "note" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "experiments"."dim_liquid_cultures" (
  "liquid_culture_id" SERIAL PRIMARY KEY,
  "medium_id" int,
  "medium_amount" float,
  "medium_unit" text,
  "starter_id" int,
  "starter_amount" float,
  "starter_unit" text,
  "disinfectant_id" int,
  "container_area_mm2" float,
  "container_area_shape" text,
  "container_height_mm" float,
  "container_type" text,
  "note" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "experiments"."dim_grain_spawn" (
  "grain_spawn_id" SERIAL PRIMARY KEY,
  "medium_id" int,
  "medium_amount" float,
  "midium_unit" text,
  "starter_id" int,
  "starter_amount" float,
  "starter_unit" text,
  "disinfectant_id" int,
  "container_area_mm2" float,
  "container_area_shape" text,
  "container_height_mm" float,
  "container_type" text,
  "note" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "experiments"."dim_blocks" (
  "block_id" SERIAL PRIMARY KEY,
  "medium_id" int,
  "medium_amount" float,
  "medium_unit" text,
  "starter_id" int,
  "starter_amount" float,
  "starter_unit" text,
  "disinfectant_id" int,
  "container_area_mm2" float,
  "container_area_shape" text,
  "container_height_mm" float,
  "container_type" text,
  "note" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "experiments"."fct_agar_plates" (
  "agar_plate_id" int,
  "date_time" timestamp DEFAULT (now()),
  "growth_culture_perc" float4 DEFAULT 0,
  "growth_contamination_perc" float4 DEFAULT 0,
  "treatment" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now()),
  PRIMARY KEY ("agar_plate_id", "date_time")
);

CREATE TABLE "experiments"."fct_liquid_cultures" (
  "liquid_culture_id" int,
  "date_time" timestamp DEFAULT (now()),
  "growth_culture_perc" float4 DEFAULT 0,
  "growth_contamination_perc" float4 DEFAULT 0,
  "treatment" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now()),
  PRIMARY KEY ("liquid_culture_id", "date_time")
);

CREATE TABLE "experiments"."fct_grain_spawn" (
  "grain_spawn_id" int,
  "date_time" timestamp DEFAULT (now()),
  "growth_culture_perc" float4 DEFAULT 0,
  "growth_contamination_perc" float4 DEFAULT 0,
  "treatment" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now()),
  PRIMARY KEY ("grain_spawn_id", "date_time")
);

CREATE TABLE "experiments"."fct_blocks" (
  "block_id" int,
  "date_time" timestamp DEFAULT (now()),
  "growth_culture_perc" float4 DEFAULT 0,
  "growth_contamination_perc" float4 DEFAULT 0,
  "treatment" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now()),
  PRIMARY KEY ("block_id", "date_time")
);

CREATE TABLE "experiments"."fct_yields" (
  "fruit_id" int,
  "block_id" int,
  "date_time" timestamp DEFAULT (now()),
  "diameter_mm" float,
  "height_mm" float,
  "yield_g" float,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "sites"."dim_sites" (
  "site_id" SERIAL PRIMARY KEY,
  "site_name" text,
  "site_type" text,
  "num_shelves" int,
  "shelf_area_total_cm2" float,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "sites"."fct_site_contents" (
  "site_id" int,
  "experiment_id" int,
  "date_inserted" date,
  "date_removed" date,
  "shelf" int,
  "shelf_row" int,
  "position" int,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "sites"."fct_site_environment" (
  "site_id" int,
  "measurement_taken_at" timestamp,
  "variable" text,
  "val" float,
  "unit" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes"."dim_recipes" (
  "recipe_id" SERIAL PRIMARY KEY,
  "recipe_name" text,
  "recipe_type" text,
  "instructions" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes"."dim_ingredients" (
  "ingredient_id" SERIAL PRIMARY KEY,
  "ingredient_name" text,
  "unit" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes"."fct_recipes" (
  "recipe_id" int,
  "ingredient_id" int,
  "proportion" float,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes"."fct_ingredients_nutrition" (
  "ingredient_id" int,
  "nutrient" text,
  "concentration" text,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

CREATE TABLE "recipes"."fct_ingredients_purchased" (
  "ingredient_id" int,
  "date_day" date,
  "price" float,
  "quantity" float,
  "row_created_at" timestamp DEFAULT (now()),
  "row_updated_at" timestamp DEFAULT (now())
);

ALTER TABLE "experiments"."dim_agar_plates" ADD FOREIGN KEY ("medium_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_agar_plates" ADD FOREIGN KEY ("starter_id") REFERENCES "experiments"."dim_strains" ("strain_id");

ALTER TABLE "experiments"."dim_agar_plates" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_agar_plates" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "experiments"."dim_liquid_cultures" ADD FOREIGN KEY ("medium_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_liquid_cultures" ADD FOREIGN KEY ("starter_id") REFERENCES "experiments"."dim_agar_plates" ("agar_plate_id");

ALTER TABLE "experiments"."dim_liquid_cultures" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_liquid_cultures" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "experiments"."dim_grain_spawn" ADD FOREIGN KEY ("medium_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_grain_spawn" ADD FOREIGN KEY ("starter_id") REFERENCES "experiments"."dim_liquid_cultures" ("liquid_culture_id");

ALTER TABLE "experiments"."dim_grain_spawn" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_grain_spawn" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "experiments"."dim_blocks" ADD FOREIGN KEY ("medium_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_blocks" ADD FOREIGN KEY ("starter_id") REFERENCES "experiments"."dim_grain_spawn" ("grain_spawn_id");

ALTER TABLE "experiments"."dim_blocks" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "experiments"."dim_blocks" ADD FOREIGN KEY ("disinfectant_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "experiments"."fct_agar_plates" ADD FOREIGN KEY ("agar_plate_id") REFERENCES "experiments"."dim_agar_plates" ("agar_plate_id");

ALTER TABLE "experiments"."fct_liquid_cultures" ADD FOREIGN KEY ("liquid_culture_id") REFERENCES "experiments"."dim_liquid_cultures" ("liquid_culture_id");

ALTER TABLE "experiments"."fct_grain_spawn" ADD FOREIGN KEY ("grain_spawn_id") REFERENCES "experiments"."dim_grain_spawn" ("grain_spawn_id");

ALTER TABLE "experiments"."fct_blocks" ADD FOREIGN KEY ("block_id") REFERENCES "experiments"."dim_blocks" ("block_id");

ALTER TABLE "experiments"."fct_yields" ADD FOREIGN KEY ("block_id") REFERENCES "experiments"."dim_blocks" ("block_id");

ALTER TABLE "sites"."fct_site_contents" ADD FOREIGN KEY ("site_id") REFERENCES "sites"."dim_sites" ("site_id");

ALTER TABLE "sites"."fct_site_contents" ADD FOREIGN KEY ("experiment_id") REFERENCES "experiments"."dim_blocks" ("block_id");

ALTER TABLE "sites"."fct_site_contents" ADD FOREIGN KEY ("experiment_id") REFERENCES "experiments"."dim_grain_spawn" ("grain_spawn_id");

ALTER TABLE "sites"."fct_site_contents" ADD FOREIGN KEY ("experiment_id") REFERENCES "experiments"."dim_liquid_cultures" ("liquid_culture_id");

ALTER TABLE "sites"."fct_site_contents" ADD FOREIGN KEY ("experiment_id") REFERENCES "experiments"."dim_agar_plates" ("agar_plate_id");

ALTER TABLE "sites"."fct_site_environment" ADD FOREIGN KEY ("site_id") REFERENCES "sites"."dim_sites" ("site_id");

ALTER TABLE "recipes"."fct_recipes" ADD FOREIGN KEY ("recipe_id") REFERENCES "recipes"."dim_recipes" ("recipe_id");

ALTER TABLE "recipes"."fct_recipes" ADD FOREIGN KEY ("ingredient_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "recipes"."fct_ingredients_nutrition" ADD FOREIGN KEY ("ingredient_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");

ALTER TABLE "recipes"."fct_ingredients_purchased" ADD FOREIGN KEY ("ingredient_id") REFERENCES "recipes"."dim_ingredients" ("ingredient_id");
