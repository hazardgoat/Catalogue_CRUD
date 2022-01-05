# Catalogue CRUD Application

***WORK IN PROGRESS***

This program creates a relational SQL database hosted on the Snowflake platform, then opens a CRUD GUI using tkinter to manipulate and view the data. In this application, it is used as a book cataloge.

**Features:**
1) Bulk uploads via CSV files to establish the primary catalogue
2) Individual entries on a given table may be added, updated, and deleted via the GUI interface. 
3) Users may download files hosted in a Box repository via the Box file ID, or both the file name and extention.
4) Current table is displayed in a tree view to the right of the text fields within the GUI.
5) Display refreshes with each action taken via the GUI so as to keep displayed info current.

**Planned Updates:**
1) Correct update behavior of the author and genre tables so that rows are updated individually.
2) Add a frame for each table so that text fields change depending on which table a User is editing.
3) Download location specified within GUI
4) Bulk table update
5) Custom queries
