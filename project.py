import sqlite3 as s3
import pandas as pd
conn = s3.connect('level3_final_project_library.db')
db_checkouts = pd.read_sql_query('''
    SELECT 
        checkouts.checkout_id,
        checkouts.member_id,
        checkouts.book_id,
        checkouts.checkout_date,
        checkouts.return_date,
        members.first_name,
        members.last_name,
        members.grade,
        members.neighborhood,
        members.membership_status,
        members.join_date
    FROM checkouts
    LEFT JOIN members ON checkouts.member_id = members.member_id
''', conn)
books_info = pd.read_json('level3_final_project_book_catalog.json')
main_db_df = pd.merge(db_checkouts, books_info, on = 'book_id', how = 'left')
web_table = pd.read_html('level3_final_project_event_signup.html')[0]
web_table = web_table.rename(columns = {
    'Member ID': 'member_id',
    'Book ID': 'book_id',
    'Checkout Date': 'checkout_date'
})
all_members = pd.read_sql_query("SELECT * FROM members", conn)
web_table = pd.merge(web_table, all_members, on = 'member_id', how = 'left')
web_table = pd.merge(web_table, books_info, on = 'book_id', how = 'left')
combined = pd.concat([main_db_df, web_table], ignore_index = True)
combined.to_csv('task1_combined_data.csv', index = False)

df_to_clean = combined.copy()
df_to_clean = df_to_clean.drop_duplicates() #removing duplicates from the raw dataset before applying the modifications
# for orphan records, I will change the values to unknown whenever a child in another table attempts to reference a parent in another table where the primary key to connect them is missing in the other table so it is illogical
orphan_records_mask = df_to_clean['first_name'].isnull()
df_to_clean.loc[orphan_records_mask, ['first_name', 'last_name', 'neighborhood']] = "Unknown"
df_to_clean.loc[orphan_records_mask, 'membership_status'] = 'N/A or Guest'
df_to_clean.loc[orphan_records_mask, 'join_date'] = 'N/A'
df_to_clean['join_date'] = df_to_clean['join_date'].fillna('Unknown')
# Starting the cleaning process for task 2, I will assume the main problems where the ones listed in the Webinar's powerpoint presentation
# So I will clean missing values, duplicates, formatting rules issues, and orphan records.
for col in df_to_clean.columns:
    if col in ['checkout_id', 'member_id', 'book_id', 'checkout_date', 'return_date', 'grade', 'first_name', 'last_name', 'publication_year']: # These don't have a mean or a median or anything of the like so autofilling them is a bad idea
        continue     
    
    if df_to_clean[col].dtype == 'str':
        df_to_clean[col] = df_to_clean[col].fillna(df_to_clean[col].mode()[0])
    elif df_to_clean[col].dtype in ['float64', 'int64']:
        df_to_clean[col] = df_to_clean[col].fillna(df_to_clean[col].mean())
df_to_clean['publication_year'] = df_to_clean['publication_year'].fillna(df_to_clean['publication_year'].mode()[0]).astype(int)
df_to_clean['return_date'] = pd.to_datetime(df_to_clean['return_date'], format = 'mixed')        # I kinda converted them to dateTime series type because they were stringified which would really prevent future date/Time Operations
df_to_clean['checkout_date'] = pd.to_datetime(df_to_clean['checkout_date'], format = 'mixed')        
# cleaning formatting errors
df_to_clean['membership_status'] = df_to_clean['membership_status'].replace({
    'active': 'Active',
    'inactive': 'Inactive'
    })
df_to_clean['neighborhood'] = df_to_clean['neighborhood'].replace({
    'NASR CITY' : 'Nasr City',
    'HELIOPOLIS' : 'Heliopolis',
    'zamalek': 'Zamalek'
}).str.strip()
df_to_clean.to_csv('task2_cleaned_data.csv', index = False)