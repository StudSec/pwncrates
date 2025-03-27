## Change log

#### 0.0 -> 1.0
- Implemented `pwncrates` table, meant to store information specific to the application.
- Added the option for case-insensitive flags in the `challenges` table, defaulting to False

#### 1.1 -> 1.2
- Added the `admins` table containing only one field which is the user_id referencing the `users` table. 
- Added the `hidden_users` table containing only one field which is the user_id referencing the `users` table.