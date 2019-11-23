import psycopg2


class connector_util():
    def __init__(self, config: Dict):
        try:
            connection = psycopg2.connect(
                user=config['pg']['user'],
                password=config['pg']['password'],
                host=config['pg']['host'],
                port=config['pg']['port'],
                database=config['pg']['database']
            )
            if (connection):
                print("Connected to postgres successfully!")
            self.cursor = connection.cursor()
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

    def check_in(self, emp_id):
        query_insert_check_in = """ INSERT INTO 
                        hr_attendance(employee_id,check_in,create_uid,create_date,write_uid,write_date) 
                        VALUES (""" + emp_id + ",now(),2,now(),2,now());"
        try:
            self.cursor.execute(query_insert_check_in)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

    def check_out(self, emp_id):
        query_update_check_out = """ UPDATE hr_attendance   
                                    SET check_out = now(), worked_hours = EXTRACT(EPOCH FROM now()-check_in)/3600
                                    WHERE employee_id =""" + emp_id + ";"
        try:
            self.cursor.execute(query_update_check_out)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
