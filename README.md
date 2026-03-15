**Research Paper Portal**

This project caters to the Department of Computer Science & Engineering, Graphic Era University.

It fetches the details of the faculties from their accounts on Scopus, displays all their details and links their research papers.

The admin login gives right for editing the data while user login is only for view purposes.

The site is updated automatically every 12 hours, to ensure timely updation. This will be done using Celery and Redis.

__Database Setup (Supabase PostgreSQL)__

This project uses Supabase (cloud PostgreSQL) as the database to store faculty information, publications, and research metrics. 
The database schema is designed based on the ER diagram and implemented using Django models.
