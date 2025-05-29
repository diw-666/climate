with source as (
    select * from {{ source('climate_data', 'climate_data') }}
),

renamed as (
    select
        station_id,
        year,
        month,
        day,
        avg_temperature,
        max_temperature,
        min_temperature,
        avg_humidity,
        total_rainfall,
        avg_wind_speed,
        -- Add any additional transformations here
        case
            when avg_temperature > 30 then 'Hot'
            when avg_temperature < 20 then 'Cold'
            else 'Moderate'
        end as temperature_category
    from source
)

select * from renamed 