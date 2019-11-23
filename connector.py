import psycopg2
import pgpubsub
import shutil
import json
from queue import Queue
from typing import Dict


def connector(queue: Queue, config: Dict):
    # Insert function and trigger to database
    try:
        connection = psycopg2.connect(
            user=config.pg.user,
            password=config.pg.password,
            host=config.pg.host,
            port=config.pg.port,
            database=config.pg.database
        )
        if (connection):
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

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    pubsub = pgpubsub.connect(user='postgres', database='odooDatabase', password='postgres')
    if (pubsub):
        print("Server is listening...")

    pubsub.listen('"insertCaugthNotify"')

    for e in pubsub.events():
        print(e.payload)
        id, path = e.payload.split(',')
        employee_name_query = "SELECT name FROM hr_employee WHERE id = " + id + ";"
        cursor.execute(employee_name_query)
        # cursor.execute("SELECT name FROM hr_employee WHERE id = %s ;", (id))
        record = cursor.fetchone()
        for attribute in record:
            print(attribute)
            emp_name = attribute

        source_path = config.path.source + '/' + path
        destination_path = config.path.dest + '/' + emp_name + '.jpg'

        print(source_path)
        print(destination_path)

        dest = shutil.copy(source_path, destination_path)
        queue.put(destination_path)
        print(dest)


if __name__ == "__main__":
    config = {}

    with open('config.json') as json_file:
        config = json.load(json_file)

    connector(Queue(), config)
