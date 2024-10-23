import sys
import re
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

    # Locate "create" or "alter" and "table" in the SQL list to handle CREATE TABLE and ALTER TABLE statements
    if any(keyword in map(str.casefold, sql_list) for keyword in ["create", "alter"]) and "table" in map(str.casefold, sql_list):
        index_table = [token.lower() for token in sql_list].index("table")
        
        # Extract table name if available after "table" keyword
        if index_table + 1 < len(sql_list):
            table_name = sql_list[index_table + 1]

            # Check for the "CONSTRAINT" keyword and ensure "FOREIGN KEY" follows
            if "constraint" in map(str.casefold, sql_list) and "foreign" in map(str.casefold, sql_list) and "key" in map(str.casefold, sql_list):
                error_constraint_name = []
                index = []
                for t in sql_list:
                    t = t.lower()
                    index_constraint = [token.lower() for token in sql_list].index(str(t.lower()))
                    if t == "constraint":
                        index_constraint_name = index_constraint + 1
                        constraint_name = sql_list[index_constraint_name]
                        index_foreign = [token.lower() for token in sql_list].index("foreign")
                        if index_constraint + 2 == index_foreign:
                            error_constraint_name.append(str(constraint_name))
                liquibase_status.fired = True
                status_message = f"Foreign key constraint name(s) '{error_constraint_name}' in table '{table_name}' does not start with 'XFK'."
                liquibase_logger.warning(status_message)
                liquibase_status.message = status_message
                sys.exit(1)

                    #if t.lower() == "constraint" and  index_constraint + 2 == "FOREIGN":
                    #   constraint_name = sql_list[index_constraint + 1]
                    #   if not constraint_name.startswith("XFK"):
                    #       error_constraint_name =+ constraint_name
                           #liquibase_status.fired = True
                           #status_message = f"Foreign key constraint name(s) '{error_constraint_name}' in table '{table_name}' does not start with 'XFK'."
                           #liquibase_logger.warning(status_message)
                           #liquibase_status.message = status_message
                           #sys.exit(1)

# Default return code
False
