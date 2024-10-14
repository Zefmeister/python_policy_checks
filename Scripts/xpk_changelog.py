### This script checks if the primary key constraint names start with "XPK_"
### Notes:
### 1. Only basic CREATE TABLE statements are supported

import sys
import liquibase_utilities

### Retrieve log handler
### Ex. liquibase_logger.info(message)
liquibase_logger = liquibase_utilities.get_logger()

### Retrieve status handler
liquibase_status = liquibase_utilities.get_status()

### Retrieve all changes in changeset
changes = liquibase_utilities.get_changeset().getChanges()

### Loop through all changes
for change in changes:

    ### Generate SQL for the change and split it into a list of strings
    sql_list = liquibase_utilities.generate_sql(change).split()

    ### Locate "create" and "table" in the SQL list to handle CREATE TABLE statements
    if "create" in map(str.casefold, sql_list) and "table" in map(str.casefold, sql_list):
        index_table = [token.lower() for token in sql_list].index("table")
        
        ### Extract table name if available after "table" keyword
        if index_table + 1 < len(sql_list):
            table_name = sql_list[index_table + 1]

            ### Check for the primary key constraint in the SQL list
            if "constraint" in map(str.casefold, sql_list):
                index_constraint = [token.lower() for token in sql_list].index("constraint")
                
                ### Extract constraint name if available after "constraint" keyword
                if index_constraint + 1 < len(sql_list):
                    constraint_name = sql_list[index_constraint + 1]
                    
                    ### Check if the constraint name starts with "XPK_"
                    if not constraint_name.startswith("XPK_"):
                        liquibase_status.fired = True
                        status_message = f"Primary key constraint name '{constraint_name}' in table '{table_name}' does not start with 'XPK_'."
                        liquibase_logger.warning(status_message)
                        liquibase_status.message = status_message
                        sys.exit(1)

### Default return code
False
