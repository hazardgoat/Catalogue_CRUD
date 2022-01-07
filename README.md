# Catalogue CRUD Application

![z](https://user-images.githubusercontent.com/74040471/148165533-105dbd8c-b06b-4267-8516-92160d32c35e.png)

***--- WORK IN PROGRESS ---***

This program creates a relational SQL database hosted on the Snowflake platform, then opens a CRUD GUI to manipulate and view the data. In this application, it is used as a book cataloge.

The requirements and primary catalogue files are located in the [Resources](https://github.com/hazardgoat/Catalogue_CRUD/tree/main/Resources) folder.

Also required: [Snowflake account](https://signup.snowflake.com/), [Box account](https://account.box.com/login), [Box Dev App](https://developer.box.com/)

**Features:**
1) Bulk uploads via CSV files to establish the primary catalogue
2) Individual entries on a given table may be added, updated, and deleted via the GUI interface. 
3) Users may download files hosted in a Box repository via the Box file ID, or both the file name and extention.
4) Current table is displayed in a tree view to the right of the text fields within the GUI.
5) Display refreshes with each action taken via the GUI so as to keep displayed info current.
