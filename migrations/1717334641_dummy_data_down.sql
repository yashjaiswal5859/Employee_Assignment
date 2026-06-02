-- DOWN: Delete dummy data
DELETE FROM employees WHERE email IN (
    'john.doe@example.com',
    'jane.smith@example.com',
    'mike.johnson@example.com',
    'sarah.williams@example.com',
    'tom.brown@example.com'
);
