INSERT INTO {{ table_name }} ({{ fields }})
VALUES ({{ values_placeholders }})
ON DUPLICATE KEY UPDATE
{{ update_fields }};