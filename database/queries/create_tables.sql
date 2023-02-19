create table raw_recipes (
    created_at timestamp,
    recipe_filename varchar,
    recipe_title varchar,
    ingredients_str varchar,
    instructions_str varchar
);

create table raw_sensor_readings (
    site varchar,
    taken_at date,
    sensor varchar,
    variable varchar,
    unit varchar,
    value float
);

create table raw_experiments (
    date_observed date,
    date_created date,
    date_terminated date,
    experiment_type varchar,
    experiment_replicate_id	int,
    starter_created_at date,
    starter_replicate_id int,
    starter_amount float,
    starter_unit varchar,
    recipe varchar,
    experiment_weight float,
    note varchar
);

create table raw_yields (
  experiment_create_at date,
  experiment_replicate_id int,
  date_harvested date,
  fruiting_body_id int,
  fruiting_body_weight float
);