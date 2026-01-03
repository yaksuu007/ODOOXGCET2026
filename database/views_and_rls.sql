CREATE VIEW public_directory AS
SELECT full_name, work_email, department, job_title, profile_pic_url
FROM users
WHERE account_status = 'Active';