create or replace function update_modified_column()
returns trigger as $$
    begin
        new.updated_at = now();
        return new;
    end;
    $$ language 'plpgsql';

create table raw_recipes (
    imported_at timestamp default now(),
    updated_at timestamp default imported_at,
    recipe_filename varchar,
    recipe_title varchar,
    ingredients_str varchar,
    instructions_str varchar
);

create trigger update_raw_recipes_update_timestamp before update on raw_recipes for each row execute procedure update_modified_column();

create table raw_sensor_readings (
    imported_at timestamp default now(),
    updated_at timestamp default imported_at,
    site varchar,
    taken_at date,
    sensor varchar,
    variable varchar,
    unit varchar,
    value float
);

create trigger update_raw_sensor_readings_update_timestamp before update on raw_sensor_readings for each row execute procedure update_modified_column();

create table raw_experiments (
    created_at timestamp default now(),
    updated_at timestamp default created_at,
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

create trigger update_raw_experiments_update_timestamp before update on raw_experiments for each row execute procedure update_modified_column();

create table raw_yields (
    created_at timestamp default now(),
    updated_at timestamp default created_at,
    experiment_created_at date,
    experiment_replicate_id int,
    date_harvested date,
    fruiting_body_id int,
    fruiting_body_weight float
);

create trigger update_raw_yields_update_timestamp before update on raw_yields for each row execute procedure update_modified_column();