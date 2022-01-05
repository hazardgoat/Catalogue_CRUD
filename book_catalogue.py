import snowflake.connector as sf
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from boxsdk import OAuth2, Client
import pandas as pd
import os
from tkinter import*
import tkinter.ttk as ttk
import tkinter.messagebox as tkMessageBox



tables_ls = ["subgenre", "genre", "author", "file", "book"]
book_cols = ["title", "series", "genre_id", "author_id", "description", "language", "publisher", "year", "isbn", "file_id"]
genre_cols = ["genre", "subgenre_id"]
subgenre_cols = ["subgenre"]
author_cols = ["author_first_name", "author_middle_name", "author_last_name"]
file_cols = ["file_name", "file_ext", "box_id"]
table_cols = [subgenre_cols, genre_cols, author_cols, file_cols, book_cols]

box_folder_id = 'xxxxxxxxxxxx'
client_id = 'xxxxxxxxxxxx'
client_secret = 'xxxxxxxxxxxx'
developer_token = 'xxxxxxxxxxxx'

user = 'xxxxxxxxxxxx'
password = 'xxxxxxxxxxxx'
account = 'xxxxxxxxxxxx'
warehouse = 'compute_wh'
database = 'MY_LIBRARY'
schema = 'BOOK_LIBRARY'

conn = sf.connect(account = account, 
                    user = user,
                    password = password,
                    warehouse = warehouse,
                    database = database,
                    schema = schema)
print("Got the context object")

cur = conn.cursor()
print("Got the cursor object")

engine = create_engine(URL(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        ))
engine_conn = engine.connect()


delete_db = False
create_db = False
interact_db = True



class Database_Setup():
    def Create_Database(self, tables=tables_ls):
        cur.execute("CREATE DATABASE IF NOT EXISTS {}".format(database))
        cur.execute("USE DATABASE {}".format(database))
        # above line has to be executed before the below, as while building the basic structure of Database and Warehouse should be present
        cur.execute("CREATE SCHEMA IF NOT EXISTS {}".format(schema))
        # Using the Database, Schema, and Warehouse
        cur.execute("USE DATABASE {}".format(database))
        cur.execute("USE SCHEMA {}.{}".format(database, schema))

        for table in tables:
            if table == "subgenre":
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS {} 
                        (
                        id INT AUTOINCREMENT,
                        {} VARCHAR(255),
                        PRIMARY KEY (id)
                        )
                    """
                    .format(table, subgenre_cols[0], subgenre_cols[0])
                )
            elif table == "genre":
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS {} 
                        (
                        id INT AUTOINCREMENT,
                        {} VARCHAR(255),
                        {} INT,
                        PRIMARY KEY (id),
                        CONSTRAINT fk_subgenre_id FOREIGN KEY ({}) REFERENCES {} (id) ON DELETE SET NULL ON UPDATE SET NULL
                        )
                    """
                    .format(table, genre_cols[0], genre_cols[1], genre_cols[1], tables[0])
                )
            elif table == 'author':
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS {} 
                        (
                        id INT AUTOINCREMENT,
                        {} VARCHAR(255),
                        {} VARCHAR(255),
                        {} VARCHAR(255),
                        PRIMARY KEY (id)
                        )
                    """
                    .format(table, author_cols[0], author_cols[1], author_cols[2])
                )
            elif table == 'file':
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS {} 
                        (
                        id INT AUTOINCREMENT,
                        {} VARCHAR(255),
                        {} VARCHAR(255),
                        {} VARCHAR(255),
                        PRIMARY KEY (id)
                        )
                    """
                    .format(table, file_cols[0], file_cols[1], file_cols[2])
                )
            else:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS {} 
                        (
                        id INT NOT NULL AUTOINCREMENT, 
                        {} VARCHAR(255), 
                        {} VARCHAR(255),
                        {} INT,
                        {} INT,
                        {} TEXT,
                        {} VARCHAR(255),
                        {} VARCHAR(255),
                        {} VARCHAR(4),
                        {} VARCHAR(13),
                        {} INT,
                        PRIMARY KEY (id),
                        CONSTRAINT fk_genre_subgenre_id FOREIGN KEY ({}) REFERENCES {} (id) ON DELETE SET NULL ON UPDATE SET NULL,
                        CONSTRAINT fk_author_names_id FOREIGN KEY ({}) REFERENCES {} (id) ON DELETE SET NULL ON UPDATE SET NULL,
                        CONSTRAINT fk_file_info_id FOREIGN KEY ({}) REFERENCES {} (id) ON DELETE SET NULL ON UPDATE SET NULL
                        )
                    """
                    .format(table, book_cols[0], book_cols[1], book_cols[2], book_cols[3], book_cols[4], book_cols[5], book_cols[6], book_cols[7], book_cols[8], book_cols[9], book_cols[2], tables[1], book_cols[3], tables[2], book_cols[9], tables[3])
                )
        conn.commit()


    def Load_Library(self, tables=tables_ls):
        main_dir = r"C:\Users\USER\Desktop\Catalogue_Tables"
        for table in tables:
            file_name = "{}.csv".format(table)
            file_path = os.path.join(main_dir, file_name)

            df = pd.read_csv(file_path, sep=',')
            df.to_sql('{}'.format(table), con=engine, index=False, if_exists='append')
        conn.commit()


    def Delete_Database(self):
        cur.execute("DROP DATABASE MY_LIBRARY")
        cur.close()     
        conn.close()



class Database_Management():
    def Add_Records(self, tables=tables_ls, table_columns=table_cols):
        txt_result = app.Text_Result()
        crud_fields = app.Crud()
        field_values = []
        for field in crud_fields:
            field_values.append(field.get())

        null_values = ["", '', ' ', " "]
        if  field_values[2] in null_values:
            txt_result.config(text="Title must be entered!", fg="red")
        else:
            for table, cols in zip(tables, table_columns):
                if table == 'subgenre':
                    try:
                        cur.execute("SELECT * FROM {} WHERE {}='{}'".format(table, subgenre_cols[0], field_values[5]))
                        cur.fetchone()[1]
                        print('Subgenre already exists...skipping')
                        skip = True
                    except:
                        col_values = [field_values[3]]
                        skip = False

                elif table == 'genre':
                    cur.execute("SELECT * FROM {} WHERE {}='{}'".format(tables[0], subgenre_cols[0], field_values[5]))
                    subgenre_id = cur.fetchone()[0]
                    try:
                        cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}')".format(table, table, field_values[4], genre_cols[1], int(subgenre_id)))
                        cur.fetchone()[1]
                        print('Genre already exists...skipping')
                        skip = True
                    except:
                        col_values = [field_values[4], subgenre_id]
                        skip = False

                elif table == 'author':
                    try:
                        cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}' AND {}='{}')".format(table, author_cols[0], field_values[6], author_cols[1], field_values[7], author_cols[2], field_values[8]))
                        cur.fetchone()[1]
                        cur.fetchone()[2]
                        cur.fetchone()[3]
                        skip = True
                    except:
                        col_values = [field_values[6], field_values[7], field_values[8]]
                        skip = False

                elif table == 'file':
                    try:
                        cur.execute("SELECT * FROM {} WHERE {}='{}'".format(table, file_cols[0], field_values[15]))
                        int(cur.fetchone()[2])
                        print('File info already exists...skipping')
                        skip = True
                    except:
                        pass
                    else: 
                        auth = OAuth2(
                            client_id=client_id,
                            client_secret=client_secret,
                            access_token=developer_token,
                        )
                        client = Client(auth)
                        items = client.search().query(query=field_values[14], limit=1, ancestor_folder_ids=[box_folder_id], file_extensions=[field_values[15]])
                        for item in items:
                            box_id = item.id

                        col_values = [field_values[14], field_values[15], box_id]
                        skip = False
                    finally:
                        print('Not enough file info provided...skipping')
                        col_values = ['', '', '']

                elif table == 'book':
                    cur.execute("SELECT * FROM {} WHERE {}='{}'".format(tables[0], subgenre_cols[0], field_values[5]))
                    subgenre_id = int(cur.fetchone()[0])
                    cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}')".format(tables[1], genre_cols[0], field_values[4], genre_cols[1], subgenre_id))
                    genre_id = cur.fetchone()[0]
                    cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}' AND {}='{}')".format(tables[2], author_cols[0], field_values[6], author_cols[1], field_values[7], author_cols[2], field_values[8]))
                    author_id = cur.fetchone()[0]
                    cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}')".format(tables[3], file_cols[0], field_values[14], file_cols[1], field_values[15]))
                    file_id = cur.fetchone()[0]

                    try:
                        cur.execute("SELECT * FROM {} WHERE ({}='{}' AND {}='{}')".format(table, book_cols[0], field_values[2], book_cols[8], field_values[13]))
                        cur.fetchone()[0]
                        print('Book already exists...skipping')
                        skip = True
                    except:
                        col_values = [field_values[2], field_values[3], genre_id, author_id, field_values[9], field_values[10], field_values[11], field_values[12], field_values[13], file_id]
                        skip = False

                if skip == False:         
                    df = pd.DataFrame([col_values], columns=cols)
                    df.to_sql('{}'.format(table), con=engine, index=False, if_exists='append')
                    conn.commit()

            txt_result.config(text="Entry added to library!", fg="green")
    
        for field in crud_fields:
            field.set("")
            
        interact.Read_Records()


    def Update_Records(self, tables=tables_ls):
        crud_fields = app.Crud()
        txt_result = app.Text_Result()
        null_values = ["", '', ' ', " "]

        print('crud_fields', crud_fields)

        field_values = []
        for field in crud_fields:
            value = field.get()
            field_values.append(value)
        print(field_values)
        try:
            int(field_values[0])
            valid_id = True  
        except:
            txt_result.config(text="ID Number must be an integer!", fg="red")
            valid_id = False

        if valid_id == True:
            if field_values[1] == 'subgenre':
                if field_values[5] not in null_values:
                    cur.execute("UPDATE {} SET {}={} WHERE id='{}'".format(field_values[1], subgenre_cols[0], field_values[5], field_values[0]))
                    conn.commit()

            elif field_values[1] == 'genre':
                genre_tables = ["subgenre", "genre"]
                update_genre_cols = [subgenre_cols, genre_cols]
                if field_values[4] or field_values[5] not in null_values:
                    self.Add_Records(genre_tables, update_genre_cols)

                    cur.execute("SELECT * FROM {} WHERE {}='{}'".format(tables[0], subgenre_cols[0], field_values[5]))
                    subgenre_id = cur.fetchone()[0]

                    cur.execute("SELECT id FROM {} WHERE {}='{}' AND {}='{}'".format(tables[1], genre_cols[0], field_values[4], genre_cols[1], subgenre_id))
                    genre_id = cur.fetchone()[0]

                    cur.execute("SELECT * FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
                    current_genre_id = cur.fetchone()[0]

                    if genre_id == current_genre_id:
                        print("The entered genre info already exists for this record: Genre ID#", genre_id)

                    conn.commit()

            elif field_values[1] == 'author':
                author_values = [field_values[6], field_values[7], field_values[8]]
                for field, col in zip (author_values, author_cols):
                    if field not in null_values:
                        cur.execute("UPDATE {} SET {}={} WHERE id='{}'".format(field_values[1], col, field, field_values[0]))
                        conn.commit()

            elif field_values[1] == 'file':
                file_values = [field_values[12], field_values[13], field_values[14]]
                for value, col in zip(file_values, file_cols):
                    if value not in null_values:
                        cur.execute("UPDATE {} SET {}={} WHERE id='{}'".format(field_values[1], col, value, field_values[0]))
                        conn.commit()

            elif field_values[1] == 'book':
                book_fields = [field_values[2], field_values[3], field_values[7], field_values[8], field_values[9], field_values[10], field_values[11]]
                book_values = [book_cols[0], book_cols[1], book_cols[4], book_cols[5], book_cols[6], book_cols[7], book_cols[8]]
                for value, col in zip(book_fields, book_values):
                    if value not in null_values:
                        cur.execute("UPDATE {} SET {}='{}' WHERE id='{}'".format(field_values[1], col, value, field_values[0]))

                genre_tables = ["subgenre", "genre"]
                update_genre_cols = [subgenre_cols, genre_cols]
                if field_values[4] or field_values[5] not in null_values:
                    self.Add_Records(genre_tables, update_genre_cols)

                    cur.execute("SELECT id FROM {} WHERE {}='{}'".format(tables[0], subgenre_cols[0], field_values[5]))
                    subgenre_id = cur.fetchone()[0]

                    cur.execute("SELECT id FROM {} WHERE {}='{}' AND {}='{}'".format(tables[1], genre_cols[0], field_values[4], genre_cols[1], subgenre_id))
                    genre_id = cur.fetchone()[0]

                    try:
                        cur.execute("SELECT {} FROM {} WHERE {}='{}' AND id='{}'".format(book_cols[2], field_values[1], book_cols[2], genre_id, field_values[0]))
                        current_genre_id = cur.fetchone()[0]
                        print("The entered genre info already exists for this record")
                    except:
                        cur.execute("UPDATE {} SET {}='{}' WHERE id='{}'".format(field_values[1], book_cols[2], genre_id, field_values[0]))
                        conn.commit()

                author_values = [field_values[6], field_values[7], field_values[8]]
                for value, col in zip(author_values, author_cols):
                    if value not in null_values:
                        cur.execute("SELECT {} FROM {} WHERE id='{}'".format(book_cols[3], field_values[1], field_values[0]))
                        author_id = cur.fetchone()[0]
                        cur.execute("UPDATE {} SET {}='{}' WHERE id='{}'".format(tables[2], col, value, author_id))
                        conn.commit()

                file_values = [field_values[14], field_values[15], field_values[16]]
                for value, col in zip(file_values, file_cols):
                    if value not in null_values:
                        cur.execute("SELECT {} FROM {} WHERE id='{}'".format(book_cols[9], field_values[1], field_values[0]))
                        file_id = cur.fetchone()[0]
                        cur.execute("UPDATE {} SET {}='{}' WHERE id='{}'".format(tables[3], col, value, file_id))
                        conn.commit()
        for field in crud_fields:
            field.set("")
        interact.Read_Records()


    def Delete_Records(self):
        crud_fields = app.Crud()
        txt_result = app.Text_Result()
        field_values = []
        for field in crud_fields:
            value = field.get()
            field_values.append(value)
        print(field_values)
        if field_values[0] == '1' and field_values[1] != 'book':
            txt_result.config(text="Row 1 is reserved and cannot be deleted!", fg="red")
        else:
            if field_values[1] == tables_ls[0]:
                cur.execute("UPDATE {} SET {}='1' WHERE {}={}".format(tables_ls[1], genre_cols[1], genre_cols[1], field_values[0]))
                cur.execute("DELETE FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
            if field_values[1] == tables_ls[1]:
                cur.execute("UPDATE {} SET {}='1' WHERE {}={}".format(tables_ls[4], book_cols[2], book_cols[2], field_values[0]))
                cur.execute("DELETE FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
            if field_values[1] == tables_ls[2]:
                cur.execute("UPDATE {} SET {}='1' WHERE {}={}".format(tables_ls[4], book_cols[3], book_cols[3], field_values[0]))
                cur.execute("DELETE FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
            if field_values[1] == tables_ls[3]:
                cur.execute("UPDATE {} SET {}='1' WHERE {}={}".format(tables_ls[4], book_cols[9], book_cols[9], field_values[0]))
                cur.execute("DELETE FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
            if field_values[1] == tables_ls[4]:
                cur.execute("DELETE FROM {} WHERE id='{}'".format(field_values[1], field_values[0]))
            txt_result.config(text="Entry removed!", fg="red")
        conn.commit()
        interact.Read_Records()

    def Download_Books(self):
        null_values = ["", '', ' ', " "]

        crud_fields = app.Crud()
        field_values = []
        for field in crud_fields:
            value = field.get()
            field_values.append(value)

        auth = OAuth2(
            client_id=client_id,
            client_secret=client_secret,
            access_token=developer_token,
        )
        client = Client(auth)
    
        main_path = r"C:\Users\USER\Downloads"

        txt_result = app.Text_Result()
        try:
            if field_values[16] not in null_values:
                box_id = field_values[16]
                file_name = client.file(box_id).get().name
                file_path = os.path.join(main_path, file_name)
                with open(file_path, 'wb') as open_file:
                    client.file('{}'.format(box_id)).download_to(open_file)
                open_file.close()
            else:
                items = client.search().query(query=field_values[14], limit=1, ancestor_folder_ids=[box_folder_id], file_extensions=[field_values[15]])
                for item in items:
                    box_id = item.id
                file_name = field_values[14]+'.'+field_values[15]
                file_path = os.path.join(main_path, file_name)
                with open(file_path, 'wb') as open_file:
                    client.file('{}'.format(box_id)).download_to(open_file)
                open_file.close()
        except:
            txt_result.config(text="Box ID or both File Name & File Extention must be entered!", fg="red")



class Interact_With_Data():
    def __init__(self):
        self.tree = app.List_View()

    def Read_Records(self):
        self.tree.delete(*self.tree.get_children())
        cur.execute('''
            SELECT book.id, book.title, book.series, genre.genre, subgenre.subgenre, author.author_first_name, author.author_middle_name, author.author_last_name, book.description, book.language, book.publisher, book.year, book.isbn, file.file_name, file.file_ext, file.box_id
            FROM book
            INNER JOIN genre ON book.genre_id = genre.id
            INNER JOIN subgenre ON genre.subgenre_id = subgenre.id
            INNER JOIN author ON book.author_id = author.id
            INNER JOIN file ON book.file_id = file.id
            ORDER BY id ASC
            ''')
        fetch = cur.fetchall()
        for data in fetch:
            self.tree.insert('', 'end', values=(data))  #can also just say values=data
        #cur.close()
        #conn.close()



class Main_Application():
    def __init__(self, root):
        self.root = root
        self.Window()
        self.Top, self.Left, self.Right, self.Forms, self.Buttons = self.Frame()
        self.txt_result = self.Labels()
        self.crud_fields = self.Form_Values()
        self.Entry()
        self.Buttons_Manager()
        self.tree = self.List_View

    def Window(self):
        self.root.title("Python SQL CRUD Applition")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width/2)
        height = int(screen_height/1.6)
        self.root.geometry(f'{width}x{height}')
        self.root.resizable(True, True)

    def Form_Values(self):
        IDNUMBER = StringVar()
        TABLE = StringVar(self.root)
        TABLE.set(tables_ls[4]) # default value
        TITLE = StringVar()
        SERIES = StringVar()
        GENRE = StringVar()
        SUBGENRE = StringVar()
        AUTHOR_FIRST_NAME = StringVar()
        AUTHOR_MIDDLE_NAME = StringVar()
        AUTHOR_LAST_NAME = StringVar()
        DESCRIPTION = StringVar()
        LANGUAGE = StringVar()
        PUBLISHER = StringVar()
        YEAR = StringVar()
        ISBN = StringVar()
        FILE_NAME = StringVar()
        FILE_EXT = StringVar()
        BOX_ID = StringVar()
        crud_fields = [IDNUMBER, TABLE, TITLE, SERIES, GENRE, SUBGENRE, AUTHOR_FIRST_NAME, AUTHOR_MIDDLE_NAME, AUTHOR_LAST_NAME, DESCRIPTION, LANGUAGE, PUBLISHER, YEAR, ISBN, FILE_NAME, FILE_EXT, BOX_ID]
        
        return crud_fields

    def Frame(self):
        Top = Frame(self.root, width=900, height=50, bd=8)
        Top.pack(side=TOP)
        Left = Frame(self.root, width=300, height=500, bd=8)
        Left.pack(side=LEFT)
        Right = Frame(self.root, width=600, height=500, bd=8, relief="raise")
        Right.pack(side=RIGHT)
        Forms = Frame(Left, width=300, height=500)
        Forms.pack(side=TOP)
        Buttons = Frame(Left, width=300, height=100, bd=8)
        Buttons.pack(side=BOTTOM)

        return Top, Left, Right, Forms, Buttons

    def Labels(self):
        txt_apptitle = Label(self.Top, width=900, font=('arial', 24), text = "Python SQL CRUD Applition")
        txt_apptitle.pack()
        txt_mediaID = Label(self.Forms, text="ID:", font=('arial', 12), bd=6)
        txt_mediaID.grid(row=1, stick="e")
        txt_mediaTable = Label(self.Forms, text="Table:", font=('arial', 12), bd=6)
        txt_mediaTable.grid(row=2, stick="e")
        txt_mediaTitle = Label(self.Forms, text="Title:", font=('arial', 12), bd=6)
        txt_mediaTitle.grid(row=3, stick="e")
        txt_mediaSeries = Label(self.Forms, text="Series:", font=('arial', 12), bd=6)
        txt_mediaSeries.grid(row=4, stick="e")
        txt_mediaGenre = Label(self.Forms, text="Genre:", font=('arial', 12), bd=6)
        txt_mediaGenre.grid(row=5, stick="e")
        txt_mediaSubgenre = Label(self.Forms, text="Subgenre:", font=('arial', 12), bd=6)
        txt_mediaSubgenre.grid(row=6, stick="e")
        txt_mediaFirstName = Label(self.Forms, text="Author First Name:", font=('arial', 12), bd=6)
        txt_mediaFirstName.grid(row=7, stick="e")
        txt_mediaMiddleName = Label(self.Forms, text="Author Middle Name:", font=('arial', 12), bd=6)
        txt_mediaMiddleName.grid(row=8, stick="e")
        txt_mediaLastName = Label(self.Forms, text="Author Last Name:", font=('arial', 12), bd=6)
        txt_mediaLastName.grid(row=9, stick="e")
        txt_mediaDescription = Label(self.Forms, text="Description:", font=('arial', 12), bd=6)
        txt_mediaDescription.grid(row=10, stick="e")
        txt_mediaLanguage = Label(self.Forms, text="Language:", font=('arial', 12), bd=6)
        txt_mediaLanguage.grid(row=11, stick="e")
        txt_mediaPublisher = Label(self.Forms, text="Publisher:", font=('arial', 12), bd=6)
        txt_mediaPublisher.grid(row=12, stick="e")
        txt_mediaYear = Label(self.Forms, text="Year:", font=('arial', 12), bd=6)
        txt_mediaYear.grid(row=13, stick="e")
        txt_mediaISBN = Label(self.Forms, text="ISBN:", font=('arial', 12), bd=6)
        txt_mediaISBN.grid(row=14, stick="e")
        txt_mediaFileName = Label(self.Forms, text="File Name:", font=('arial', 12), bd=6)
        txt_mediaFileName.grid(row=15, stick="e")
        txt_mediaFileExtention = Label(self.Forms, text="File Extention:", font=('arial', 12), bd=6)
        txt_mediaFileExtention.grid(row=16, stick="e")
        txt_boxID = Label(self.Forms, text="Box ID:", font=('arial', 12), bd=6)
        txt_boxID.grid(row=17, stick="e")
        txt_result = Label(self.Buttons)
        txt_result.pack(side=TOP)

        return txt_result
    
    def Entry(self):
        mediaID = Entry(self.Forms, textvariable=self.crud_fields[0], width=30)
        mediaID.grid(row=1, column=1)
        mediaTable = Entry(self.Forms, textvariable=self.crud_fields[1], width=30)
        mediaTable.grid(row=2, column=1)
        mediaTitle = Entry(self.Forms, textvariable=self.crud_fields[2], width=30)
        mediaTitle.grid(row=3, column=1)
        mediaSeries = Entry(self.Forms, textvariable=self.crud_fields[3], width=30)
        mediaSeries.grid(row=4, column=1)
        mediaGenre = Entry(self.Forms, textvariable=self.crud_fields[4], width=30)
        mediaGenre.grid(row=5, column=1)
        mediaSubgenre = Entry(self.Forms, textvariable=self.crud_fields[5], width=30)
        mediaSubgenre.grid(row=6, column=1)
        mediaAuthor_First_Name = Entry(self.Forms, textvariable=self.crud_fields[6], width=30)
        mediaAuthor_First_Name.grid(row=7, column=1)
        mediaAuthor_Middle_Name = Entry(self.Forms, textvariable=self.crud_fields[7], width=30)
        mediaAuthor_Middle_Name.grid(row=8, column=1)
        mediaAuthor_Last_Name = Entry(self.Forms, textvariable=self.crud_fields[8], width=30)
        mediaAuthor_Last_Name.grid(row=9, column=1)
        mediaDescription = Entry(self.Forms, textvariable=self.crud_fields[9], width=30)
        mediaDescription.grid(row=10, column=1)
        mediaLanguage = Entry(self.Forms, textvariable=self.crud_fields[10], width=30)
        mediaLanguage.grid(row=11, column=1)
        mediaPublisher = Entry(self.Forms, textvariable=self.crud_fields[11], width=30)
        mediaPublisher.grid(row=12, column=1)
        mediaYear = Entry(self.Forms, textvariable=self.crud_fields[12], width=30)
        mediaYear.grid(row=13, column=1)
        mediaISBN = Entry(self.Forms, textvariable=self.crud_fields[13], width=30)
        mediaISBN.grid(row=14, column=1)
        mediaFileName = Entry(self.Forms, textvariable=self.crud_fields[14], width=30)
        mediaFileName.grid(row=15, column=1)
        mediaFileExtention = Entry(self.Forms, textvariable=self.crud_fields[15], width=30)
        mediaFileExtention.grid(row=16, column=1)
        mediaBoxID = Entry(self.Forms, textvariable=self.crud_fields[16], width=30)
        mediaBoxID.grid(row=17, column=1)

    def Buttons_Manager(self):
        btn_download = Button(self.Buttons, width=10, text="Download", command=manage.Download_Books)
        btn_download.pack(side=LEFT)
        btn_add = Button(self.Buttons, width=10, text="Add", command=manage.Add_Records)
        btn_add.pack(side=LEFT)
        #btn_update = Button(Buttons, width=10, text="Update", state=DISABLED)
        btn_update = Button(self.Buttons, width=10, text="Update", command=manage.Update_Records)
        btn_update.pack(side=LEFT)
        btn_delete = Button(self.Buttons, width=10, text="Delete", command=manage.Delete_Records)
        btn_delete.pack(side=LEFT)
        btn_exit = Button(self.Buttons, width=10, text="Exit", command=self.Exit)
        btn_exit.pack(side=LEFT)

    def List_View(self):
        scrollbary = Scrollbar(self.Right, orient=VERTICAL)
        scrollbarx = Scrollbar(self.Right, orient=HORIZONTAL)
        book_tree_cols = ['ID', 'Title', 'Series', 'Genre', 'Subgenre', 'Author First Name', 'Author Middle Name', 'Author Last Name', 'Description', 'Language', 'Publisher', 'Year', 'ISBN', 'File Name', 'File Extention', 'Box ID']
        tree = ttk.Treeview(self.Right, columns=book_tree_cols, selectmode="extended", height=500, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        i=0
        for column in book_tree_cols:
            tree.heading(column, text=column, anchor=W)
            if i == 0:
                width=0
            elif i == 1:
                width = 30
            elif i in [4,5,9]:
                width = 70
            else:
                width = 100
            tree.column('#{}'.format(i), stretch=NO, minwidth=0, width=width)
            i+=1
        tree.pack()

        return tree
    
    def Text_Result(self):
        return self.txt_result
    
    def Crud(self):
        return self.crud_fields

    def Exit():
        result = tkMessageBox.askquestion('Book Library', 'Are you sure you want to exit?', icon="warning")
        if result == 'yes':
            root.destroy()
            exit()  




if __name__ == '__main__':
    setup = Database_Setup()
    manage = Database_Management()

    if delete_db == True:
        setup.Delete_Database()
    if create_db == True:
        setup.Create_Database()
        setup.Load_Library()
    if interact_db == True:
        root = Tk()

        app = Main_Application(root)
        interact = Interact_With_Data()
        interact.Read_Records()
        
        root.mainloop()
