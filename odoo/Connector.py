import psycopg2
import pgpubsub

# Insert function and trigger to database
try:
	connection = psycopg2.connect(user="boas",
                                  password="1304513045",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="test")
	if(connection):
		print("Connected to postgres successfully!")
	cursor = connection.cursor()

	create_function_query_update = """CREATE OR REPLACE FUNCTION insertCaugthNotifyUpdate()
								  RETURNS TRIGGER AS $$
								DECLARE
								BEGIN
									IF NEW.res_field = 'image_1920' AND NEW.res_model='hr.employee' AND OLD.store_fname <> NEW.store_fname THEN
								 	 	PERFORM pg_notify('insertCaugthNotify', NEW.store_fname);
								 	 END IF;
								  RETURN NEW;
								END;
								$$ LANGUAGE plpgsql;"""

	create_function_query_insert = """CREATE OR REPLACE FUNCTION insertCaugthNotifyInsert()
								  RETURNS TRIGGER AS $$
								DECLARE
								BEGIN
									IF NEW.res_field = 'image_1920' AND NEW.res_model='hr.employee' THEN
								 	 	PERFORM pg_notify('insertCaugthNotify', NEW.store_fname);
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


pubsub = pgpubsub.connect(user='postgres', database='test', password='1304513045')
if(pubsub):
	print("Server is listening...")

pubsub.listen('"insertCaugthNotify"')

for e in pubsub.events(): 
    print (e.payload)



