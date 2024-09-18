## Queries Section2 SQL Endpoints

HIRED_EMPLOYEES_2021= """WITH QuarterlyData AS (
    SELECT 
        b.department,
        c.job,
        COUNT(a.id) AS hired_employees,
        CASE
            WHEN strftime('%m', a.datetime) IN ('01', '02', '03') THEN 'Q1'
            WHEN strftime('%m', a.datetime) IN ('04', '05', '06') THEN 'Q2'
            WHEN strftime('%m', a.datetime) IN ('07', '08', '09') THEN 'Q3'
            WHEN strftime('%m', a.datetime) IN ('10', '11', '12') THEN 'Q4'
        END AS quarter
    FROM
        hired_employees a
    LEFT JOIN
        departments b ON a.department_id = b.id
    LEFT JOIN
        jobs c ON a.job_id = c.id
    WHERE
        strftime('%Y', a.datetime) = '2021'
    GROUP BY
        b.department, c.job, quarter
)
SELECT
    department,
    job,
    SUM(CASE WHEN quarter = 'Q1' THEN hired_employees ELSE 0 END) AS Q1,
    SUM(CASE WHEN quarter = 'Q2' THEN hired_employees ELSE 0 END) AS Q2,
    SUM(CASE WHEN quarter = 'Q3' THEN hired_employees ELSE 0 END) AS Q3,
    SUM(CASE WHEN quarter = 'Q4' THEN hired_employees ELSE 0 END) AS Q4
FROM
    QuarterlyData
GROUP BY
    department, job
ORDER BY
    department, job;"""