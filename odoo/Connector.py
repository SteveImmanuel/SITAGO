# Destination path  
destination = 'D:/Kuliah/Semester 5/SI/implementasi_akhir/SITAGO/server/received_images'
# Source path  
source = 'C:/Users/ASUS/AppData/Local/OpenERP S.A/Odoo/filestore/odooDatabase'

import psycopg2
import pgpubsub
import shutil

# Insert function and trigger to database
try:
	connection = psycopg2.connect(user="postgres",
                                  password="postgres",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="odooDatabase")
	if(connection):
		print("Connected to postgres successfully!")
	cursor = connection.cursor()

	create_function_query_update = """CREATE OR REPLACE FUNCTION insertCaugthNotifyUpdate()
								  RETURNS TRIGGER AS $$
								DECLARE
								BEGIN
									IF NEW.res_field = 'image_1920' AND NEW.res_model='hr.employee' AND OLD.store_fname <> NEW.store_fname THEN
								 	 	PERFORM pg_notify('insertCaugthNotify', NEW.res_id || ',' || NEW.store_fname );
								 	 END IF;
								  RETURN NEW;
								END;
								$$ LANGUAGE plpgsql;"""

	create_function_query_insert = """CREATE OR REPLACE FUNCTION insertCaugthNotifyInsert()
								  RETURNS TRIGGER AS $$
								DECLARE
								BEGIN
									IF NEW.res_field = 'image_1920' AND NEW.res_model='hr.employee' THEN
								 	 	PERFORM pg_notify('insertCaugthNotify', NEW.res_id || ',' || NEW.store_fname );
								 	 END IF;
								  RETURN NEW;
								END;
								$$ LANGUAGE plpgsql;"""

	drop_trigger_query_update = "DROP TRIGGER IF EXISTS insertCaugthNotifyUpdate ON ir_attachment"
	drop_trigger_query_insert = "DROP TRIGGER IF EXISTS insertCaugthNotifyInsert ON ir_attachment"

	create_trigger_query_update = """CREATE TRIGGER insertCaugthNotifyUpdate
								AFTER UPDATE ON ir_attachment
								FOR EACH ROW EXECUTE PROCEDURE insertCaugthNotifyUpdate();
	"""

	create_trigger_query_insert = """CREATE TRIGGER insertCaugthNotifyInsert
								AFTER INSERT ON ir_attachment
								FOR EACH ROW EXECUTE PROCEDURE insertCaugthNotifyInsert();
	"""

	cursor.execute(create_function_query_update)
	cursor.execute(create_function_query_insert)
	print('insertCaugthNotifyUpdate() and insertCaugthNotifyInsert() function inserted')
	cursor.execute(drop_trigger_query_insert)
	cursor.execute(drop_trigger_query_update)
	cursor.execute(create_trigger_query_update)
	cursor.execute(create_trigger_query_insert)
	print('insertCaugthNotifyUpdate and insertCaugthNotifyInsert trigger inserted')
	connection.commit()

except (Exception, psycopg2.Error) as error :
    print ("Error while fetching data from PostgreSQL", error)


pubsub = pgpubsub.connect(user='postgres', database='odooDatabase', password='postgres')
if(pubsub):
	print("Server is listening...")

pubsub.listen('"insertCaugthNotify"')

for e in pubsub.events(): 
	print (e.payload)
	id, path = e.payload.split(',')
	employee_name_query = "SELECT name FROM hr_employee WHERE id = " + id + ";"
	cursor.execute(employee_name_query)
	# cursor.execute("SELECT name FROM hr_employee WHERE id = %s ;", (id))
	record = cursor.fetchone()
	for attribute in record:
		print(attribute)
		emp_name = attribute


	source_ = source + '/' +  path
	destination_ = destination + '/' + emp_name + '.jpg'
	print(source_)
	print(destination)
	dest = shutil.copy(source_, destination_)
	print(dest)



