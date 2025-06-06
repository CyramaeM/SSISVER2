from sqlite3 import Cursor
import MySQLdb
from webapp import mysql
from flask_mysqldb import MySQL
from flask import request, session, redirect, url_for, flash


class college:

    @staticmethod
    def collegehome():
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT collegecode, collegename FROM college")
        colleges = cur.fetchall()
        cur.close()
        return colleges
    
    @staticmethod
    def add_college(collegecode,collegename):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO college (collegecode, collegename) VALUES (%s, %s)", (collegecode, collegename))
        mysql.connection.commit()
        flash("College added successfully!", "success")
        cur.close()
       
    @staticmethod
    def edit_college(college_code,college_name,collegecode):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("""
                UPDATE college
                SET collegecode = %s, collegename = %s
                WHERE collegecode = %s
            """, (college_code, college_name, collegecode))

        mysql.connection.commit()
        flash("College updated successfully!", "success")
        cursor.close()

    @staticmethod
    def delete_college(college_id):
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("DELETE FROM college WHERE collegecode = %s", (college_id,))
        mysql.connection.commit()
        flash("College deleted successfully!", "success")
        cur.close()
    