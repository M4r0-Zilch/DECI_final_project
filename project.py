import sqlite3 as s3
import pandas as pd
conn = s3.connect('download.db')
query = """
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
LEFT JOIN members ON checkouts.member_id = members.member_id;
"""
db_checkouts = pd.read_sql_query(query, conn)
json_books = pd.read_json('download.json')
db_checkouts_with_books = pd.merge(db_checkouts, json_books, on='book_id', how='left')
html_tables = pd.read_html('download.html')
web_checkouts = html_tables[0]
web_checkouts = web_checkouts.rename( columns = {
    'Member ID': 'member_id',
    'Book ID': 'book_id',
    'Checkout Date': 'checkout_date'
})
members_df = pd.read_sql_query("SELECT * FROM members", conn)
web_checkouts = pd.merge(web_checkouts, members_df, on = 'member_id', how = 'left')
web_checkouts = pd.merge(web_checkouts, json_books, on = 'book_id', how = 'left')
combined_df = pd.concat([db_checkouts_with_books, web_checkouts], ignore_index = True)
combined_df.to_csv('task1_combined_data.csv', index = False)