# Setting Up MariaDB Database

First, open a command prompt and do
```bash
mysql -u root -p
```
> **Note:** You will be prompted to enter the password. (This is the same password as the one you provided during installation. It can be empty.) \
You can also replace `root` with any other mysql user if you have set it up as such.

Now once you are in the mysql promt, do
```sql
create database library;
exit;
```

Now you have setup the database. The tables and data will be created by the program.

