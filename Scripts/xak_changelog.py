import sys
import liquibase_utilities

### Retrieve log handler
### Example: liquibase_logger.info(message)
liquibase_logger = liquibase_utilities.get_logger()

### Retrieve status handler
liquibase_status = liquibase_utilities.get_status()

### Retrieve all changes in changeset
changes = liquibase_utilities.get_changeset().getChanges()

### Loop through all changes
for change in changes:

    ### Generate SQL for the change and split it into a list of strings
    sql_list = liquibase_utilities.generate_sql(change).split()

    ### Locate "create" and "index" in the SQL list to handle CREATE INDEX statements
    if "create" in map(str.casefold, sql_list) and "index" in map(str.casefold, sql_list):
        index_index = [token.lower() for token in sql_list].index("index")
        
        ### Extract index name if available after "index" keyword
        if index_index + 1 < len(sql_list):
            index_name = sql_list[index_index + 1]

            ### Check if the index name starts with "XAK_"
            if not index_name.startswith("XAK_"):
                liquibase_status.fired = True
                status_message = f"Alternate key index name '{index_name}' does not start with 'XAK_'."
                liquibase_logger.warning(status_message)
                liquibase_status.message = status_message
                sys.exit(1)

### Default return code
False
