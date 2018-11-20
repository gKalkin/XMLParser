# Author: Garrett Myers

from flask import Flask, request, render_template, make_response, redirect
from flask_restful import Resource, Api, reqparse
import xml.etree.ElementTree as ET
import re
import sqlite3

app = Flask(__name__)
api = Api(app)

class Readme(Resource):
	def get(self):
		return make_response(render_template('index.html'), 200)

class CaseList(Resource):
	def get(self):
		connection = sqlite3.connect('cases.db')
		cursor = connection.cursor()

		cursor.execute("SELECT * FROM cases")
		rows = cursor.fetchall()

		connection.close()
		return make_response(render_template('cases.html', rows=rows), 200)

class Case(Resource):
	def get(self, name):
		connection = sqlite3.connect('cases.db')
		cursor = connection.cursor()

		cmd = 'SELECT * FROM cases WHERE id = ?'
		cursor.execute(cmd, (name,))
		
		rows = cursor.fetchall()
		connection.close()

		return make_response(render_template('case_name.html', rows=rows, name=name), 200)




class NewCase(Resource):
	def get(self):
		return make_response(render_template('case_new.html'), 200)

	def post(self):
		connection = sqlite3.connect('cases.db')
		cursor = connection.cursor()

		if not cursor:
			return {'message': "Failed to connect to database. Try again."}, 500 

		create_table = "CREATE TABLE IF NOT EXISTS cases (id text, plaintiff text, defendant text)"
		cursor.execute(create_table)

		connection.commit()

		file = request.files['casefile']
		casename = request.form['casename']

		if file is None or casename is None:
			return {'message': "An XML file must be uploaded and named."}, 400

		if file is not None:
			tree = ET.parse(file)
			root = tree.getroot()

			lines = []

			for content in root.iter('*'):
				if content.text is not None:
					lines.append(str(content.text))

			case = {
				'plaintiff': '',
				'defendant': ''
			}

			plaintiff = ''
			defendant = ''
			
			#Flags for capturing plaintiff and defendant
			capPlaintiff = False
			capDef = False

			for line in lines:
				# Begin capture plaintiff after 'court of' statement
				if re.search('COURT OF', line.upper()) is not None:
					capPlaintiff = True
					continue

				# Stop capturing when vs. or v. is hit.
				if (re.search('VS?\.', line.upper()) is not None) and capPlaintiff:
					capPlaintiff = False
					capDef = True
					case['plaintiff'] = case['plaintiff'] + plaintiff
					continue

				# Stop capturing defendant when we reach "defendant"
				if (re.search('DEFENDANT', line.upper()) is not None) and capDef:
					capDef = False
					case['defendant'] = case['defendant'] + defendant
					break

				if capPlaintiff:
					plaintiff = plaintiff + line

				if capDef:
					defendant = defendant + line

			
			case_set = (casename, case['plaintiff'], case['defendant'])

			insert = "INSERT INTO cases VALUES (?, ?, ?)"
			cursor.execute(insert, case_set)
			connection.commit()	
			connection.close()

			red = 'http://127.0.0.1:5000/cases/' + casename

			return redirect(red)


		return {'message': 'No file uploaded.'}, 400


api.add_resource(Readme, '/')
api.add_resource(CaseList, '/cases')
api.add_resource(NewCase, '/cases/new')
api.add_resource(Case, '/cases/<string:name>')

app.run(port=5000)