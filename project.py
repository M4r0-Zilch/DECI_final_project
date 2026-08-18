import sqlite3 as s3
import pandas as pd
conn = s3.connect('download.db')
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
books_info = pd.read_json('download.json')
main_db_df = pd.merge(db_checkouts, books_info, on = 'book_id', how = 'left')
web_table = pd.read_html('download.html')[0]
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