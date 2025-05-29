DELETE FROM {{ table_name }}
WHERE {{ key_field }} = {{ key_value }};