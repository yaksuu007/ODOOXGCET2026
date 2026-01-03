-- Enable RLS on the Payroll table
ALTER TABLE payroll ENABLE ROW LEVEL SECURITY;

-- Create a policy: Admins can see everything, Employees only see their own
CREATE POLICY payroll_visibility_policy ON payroll
    FOR SELECT
    USING (
        (SELECT role FROM users WHERE user_id = auth.uid()) = 'HR_Admin' 
        OR 
        user_id = auth.uid()
    );