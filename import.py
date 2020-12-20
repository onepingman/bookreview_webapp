import os
import psycopg2
import csv

conn = psycopg2.connect(
    """postgres://User:Password@Host:5432/Database"""
)
cursor=conn.cursor()

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        cursor.execute("INSERT INTO books (isbn, title, author, year) VALUES (%s, %s, %s, %s)",(isbn, title, author, year))


        #print(f"Added the book named  {title} by author  {author} which was released in the year {year} .")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

