import sqlite3



def create_db(overwrite=False):
    con = sqlite3.connect("tutorial.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE name='movie'")
    if res.fetchone() is not None:
        if not overwrite:
            con.close()
            print("Movie Table already exists")
            return
        
        cur.execute("DELETE TABLE movie")
    
    # created once
    cur.execute("CREATE TABLE movie(title, year, score)") 
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('The Shawshank Redemption', 1994, 9.3)")
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('The Godfather', 1972, 9.2)")
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('The Dark Knight', 2008, 9.0)")
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('The Godfather: Part II', 1974, 9.0)")
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('The Lord of the Rings: The Return of the King', 2003, 8.9)")
    cur.execute("INSERT INTO movie(title, year, score) VALUES ('Pulp Fiction', 1994, 8.9)")
    con.commit()
    for row in cur.execute("SELECT * FROM movie ORDER BY year"):
        print(row)

    con.close()


def query_db():
    con = sqlite3.connect("tutorial.db")
    cur = con.cursor()
    for row in cur.execute("SELECT * FROM movie ORDER BY year"):
        print(row)    
    con.close()
    



query_db()