import pandas as pd
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

def generate_bulk_case_update(df, table_name="studentInfo"):
    """
    Generates a single, large UPDATE statement using CASE.
    This is much faster and database-agnostic.
    """
    if df.empty:
        print("DataFrame is empty. No query to generate.")
        return ""

    # We only need the key columns and drop any duplicates
    try:
        df_keys = df[['id_student', 'study_method_preference', 'kmeans_cluster']].drop_duplicates()
    except KeyError as e:
        print(f"Error: A required column was not found. {e}")
        print("Please ensure 'id_student', 'study_method_preference', and 'kmeans_cluster' are in the CSV.")
        return None

    ids = df_keys['id_student'].tolist()
    ids_str = ", ".join(map(str, ids))

    # Build CASE for study_method_preference
    pref_case = "CASE id_student\n"
    for _, row in df_keys.iterrows():
        # Escape single quotes in the string data
        pref_val = str(row['study_method_preference']).replace("'", "''")
        pref_case += f"    WHEN {row['id_student']} THEN '{pref_val}'\n"
    pref_case += "    ELSE study_method_preference\nEND"

    # Build CASE for kmeans_cluster (which the user called cluster_id)
    cluster_case = "CASE id_student\n"
    for _, row in df_keys.iterrows():
        cluster_case += f"    WHEN {row['id_student']} THEN {int(row['kmeans_cluster'])}\n"
    cluster_case += "    ELSE cluster_id\nEND"

    # Combine into a single query
    query = (
        f"UPDATE {table_name}\n"
        f"SET\n"
        f"    study_method_preference = {pref_case},\n"
        f"    cluster_id = {cluster_case}\n"
        f"WHERE id_student IN ({ids_str});"
    )
    
    return query

def main():
    file_path = 'student_after_clustered.csv'
    output_sql_file = 'bulk_update_query.sql'
    target_table_name = "studentInfo" # Change this to your actual table name
    
    try:
        # Load the data
        df = pd.read_csv(file_path)
        
        # Generate the single, fast bulk query
        print(f"Generating bulk update query from '{file_path}'...")
        sql_query = generate_bulk_case_update(df, target_table_name)
        
        if sql_query:
            # Write the query to a .sql file
            with open(output_sql_file, 'w', encoding='utf-8') as f:
                f.write(sql_query)
            
            print(f"Successfully generated and saved the bulk update query.")
            print(f"File created: {output_sql_file}")
            print(f"This file contains one large, efficient 'UPDATE...CASE' statement.")

    except FileNotFoundError:
        print(f"Error: The input file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the main function
main()