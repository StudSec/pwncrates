## Change log
Running changelog of the database schema. There are no strict guidelines for the naming scheme but try to adhere
to the following:
- x.0 for major changes
- 0.x for minor changes

Database migrations are performed sequentially in a linked fashion, each migration has the following name:
```
migration-version_1-version_2.sql
```
The migration takes a database of version_1 and by the end of the execution the database should be in version_2. Then
the next migration is run if it exists. This means that if there is a 'gap' in the migration scripts the later
scripts will not be run.


#### 0.0 -> 1.0
- Implemented `pwncrates` table, meant to store information specific to the application.
- Added the option for case-insensitive flags in the `challenges` table, defaulting to False

#### 1.1 -> 1.2
- Added the `admins` table containing only one field which is the user_id referencing the `users` table. 
- Added the `hidden_users` table containing only one field which is the user_id referencing the `users` table.

#### 1.2 -> 2.0
- Switched from ID's to UUID's
- Split flags and connection strings into separate tables