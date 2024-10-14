import sys
import liquibase_utilities

# Retrieve log and status handlers
liquibase_logger = liquibase_utilities.get_logger()
liquibase_status = liquibase_utilities.get_status()

# Retrieve all changes in the changeset
changes = liquibase_utilities.get_changeset().getChanges()

# Loop through all changes
for change in changes:

    # Generate SQL for the change and split it into a list of strings
    sql_list = liquibase_utilities.generate_sql(change).split()

    # Locate "create" and "table" in the SQL list to handle CREATE TABLE statements
    if "create" in map(str.casefold, sql_list) and "table" in map(str.casefold, sql_list):
        index_table = [token.lower() for token in sql_list].index("table")
        
        # Extract table name if available after "table" keyword
        if index_table + 1 < len(sql_list):
            table_name = sql_list[index_table + 1]

            # Check for the "CONSTRAINT" keyword and ensure "PRIMARY KEY" follows
            if "constraint" in map(str.casefold, sql_list) and "primary" in map(str.casefold, sql_list) and "key" in map(str.casefold, sql_list):
                index_constraint = [token.lower() for token in sql_list].index("constraint")
                index_primary = [token.lower() for token in sql_list].index("primary")
                index_key = [token.lower() for token in sql_list].index("key")

                # Ensure "KEY" comes after "PRIMARY"
                if index_key > index_primary:
                    # Ensure "PRIMARY KEY" comes after "CONSTRAINT"
                    if index_primary > index_constraint:
                        # Extract the constraint name between "CONSTRAINT" and "PRIMARY KEY"
                        if index_constraint + 1 < index_primary:
                            constraint_name = sql_list[index_constraint + 1]

                            # Check if the constraint name starts with "XPK"
                            if not constraint_name.startswith("XPK"):
                                liquibase_status.fired = True
                                status_message = f"Primary key constraint name '{constraint_name}' in table '{table_name}' does not start with 'XPK'."
                                liquibase_logger.warning(status_message)
                                liquibase_status.message = status_message
                                sys.exit(1)

# Default return code
False
