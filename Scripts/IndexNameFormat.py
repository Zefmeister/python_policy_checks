import sys
import re
import liquibase_utilities

# Retrieve log and status handlers
liquibase_logger = liquibase_utilities.get_logger()
liquibase_status = liquibase_utilities.get_status()

# Retrieve all changes in the changeset
changes = liquibase_utilities.get_changeset().getChanges()

# Function to validate foreign key constraint names
def validate_foreign_key_constraints(sql_list):
    error_constraint_name = []
    table_name = None
    
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

                # Validate that "FOREIGN" and "KEY" are present and follow "CONSTRAINT"
                if "foreign" in map(str.casefold, sql_list) and "key" in map(str.casefold, sql_list):
                    if not constraint_name.startswith("XFK"):
                        error_constraint_name.append(constraint_name)

    # Log warning if any foreign key constraint names don't meet the standard
    if error_constraint_name:
        liquibase_status.fired = True
        status_message = f"Foreign key constraint name(s) '{error_constraint_name}' in table '{table_name}' do not start with 'XFK'."
        liquibase_logger.warning(status_message)
        liquibase_status.message = status_message
        sys.exit(1)

# Function to split sql_list by changesets (ALTER/CREATE TABLE statements)
def split_changesets(sql_list):
    changeset_splits = []
    current_changeset = []

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

    return changeset_splits

# Loop through all changes
for change in changes:
    # Generate SQL for the change and split it into a list of strings
    sql_list = liquibase_utilities.generate_sql(change).split()

    # Split sql_list into separate changesets
    changesets = split_changesets(sql_list)

    # Validate each changeset for foreign key constraint names
    for changeset in changesets:
        validate_foreign_key_constraints(changeset)

# Default return code
False
