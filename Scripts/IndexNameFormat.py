import sys
import re
import liquibase_utilities

# Retrieve log and status handlers
liquibase_logger = liquibase_utilities.get_logger()
liquibase_status = liquibase_utilities.get_status()

# Retrieve all changes in the changeset
changes = liquibase_utilities.get_changeset().getChanges()

# Function to validate foreign key constraint names
def validate_foreign_key_constraints(sql_list, flag):
    table_name = None
    list_error_constraints = []
    list_error_tables = []
    # Validate that if ALTER or CREATE
    if "alter" in map(str.casefold, sql_list) and "table" in map(str.casefold, sql_list):
        change_type = "alter"
    elif "create" in map(str.casefold, sql_list) and "table" in map(str.casefold, sql_list):
        change_type = "create"
    else:
        liquibase_status.fired = True
        status_message = f"Change set does not contain a CREATE OR ALTER statements."
        liquibase_logger.warning(status_message)
        liquibase_status.message = status_message
        sys.exit(1)
        
    # Loop through sql_list to check for "ALTER TABLE" or "CREATE TABLE" statements
    for index, token in enumerate(sql_list):
        token_lower = token.lower()

        # Find table name after "table" keyword
        if token_lower == "table" and index + 1 < len(sql_list):
            table_name = sql_list[index + 1]

        # Check for "CONSTRAINT", "FOREIGN", and "KEY"
        if token_lower == "constraint":
            if index + 1 < len(sql_list):
                constraint_name = sql_list[index + 1]

                # get index for "CONSTRAINT" and "FOREIGN"
                index_constraint = [token.lower() for token in sql_list].index("constraint")
                index_foreign = [token.lower() for token in sql_list].index("foreign")

                if index_foreign == index_constraint + 2:
                    if not constraint_name.startswith("XFK"):
                        list_error_constraints =+ constraint_name
                        list_error_tables =+ table_name
                        flag = flag + 1
                    else:
                        flag = flag
    return list_error_constraints, list_error_tables, flag

# Function to split sql_list by changesets (ALTER/CREATE TABLE statements)
def split_changesets(sql_list):
    changeset_splits = []
    current_changeset = []
    # Set errorflag
    error_flag = 0
    for token in sql_list:
        if token.lower() in ["alter", "create"] and "table" in map(str.casefold, sql_list):
            # If we encounter "ALTER" or "CREATE" and the current_changeset is not empty, save it
            if current_changeset:
                changeset_splits.append(current_changeset)
                current_changeset = []
        current_changeset.append(token)

    # Append the final changeset if there is one
    if current_changeset:
        changeset_splits.append(current_changeset)

    for changeset in changeset_splits: 
        list_error_constraints, list_error_tables, error_count = validate_foreign_key_constraints(changeset, error_flag)
    if error_count != 0:
        liquibase_status.fired = True
        status_message = f"Foreign key constraint name(s) '{list_error_constraints}' in table '{list_error_tables}' do not start with 'XFK'."
        liquibase_logger.warning(status_message)
        liquibase_status.message = status_message
        sys.exit(1)

# Loop through all changes
for change in changes:
    # Generate SQL for the change and split it into a list of strings
    sql_list = liquibase_utilities.generate_sql(change).split()
    # Split sql_list into separate changesets
    split_changesets(sql_list)

# Default return code
False
