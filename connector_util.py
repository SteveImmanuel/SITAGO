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

    def insert_sale_order(self, name, amount):
        query_insert_sale_order = """INSERT INTO public.sale_order(
                                    name, state, date_order, require_signature, require_payment, 
                                    create_date, user_id, partner_id, partner_invoice_id, partner_shipping_id, 
                                    pricelist_id, invoice_status, amount_untaxed, amount_tax, amount_total, 
                                    currency_rate, company_id, team_id, create_uid, write_uid, write_date)
                                    VALUES (""" + name + """, 'draft', NOW(), true, true, 
                                            NOW(), 2, 1, 1, 1, 
                                            1, 'no',""" + amount + """, 0,""" + amount + """, 
                                            1.000000, 1, 1, 2, 2, NOW());"""
        try:
            self.cursor.execute(query_insert_sale_order)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

    def insert_sale_order_line(self, order_id, price_unit, product_uom_qty, nama_barang):
        query_find_product_id = """select product_product.id from product_product, product_template 
                                where product_product.product_tmpl_id = product_template.id 
                                AND product_template.name = '"""+ nama_barang + "'; "

        product_id = self.cursor.execute(query_find_product_id)

        query_insert_sale_order_line = """INSERT INTO public.sale_order_line(
                                        order_id, name, sequence, invoice_status, price_unit, 
                                        price_subtotal, price_tax, price_total, price_reduce, price_reduce_taxinc, 
                                        price_reduce_taxexcl, discount, product_id, product_uom_qty, product_uom, 
                                        qty_delivered_method, qty_delivered, qty_delivered_manual, qty_to_invoice, qty_invoiced, 
                                        untaxed_amount_invoiced, untaxed_amount_to_invoice, salesman_id, currency_id, company_id, 
                                        order_partner_id, state, customer_lead, create_uid, create_date, 
                                        write_uid, write_date)
                                        VALUES ("""+ order_id + """, '', 10, 'no',""" +price_unit+""", 
                                                """ + price_unit*product_uom_qty + """, 0, 2000,""" + price_unit + "," + price_unit + """, 
                                                """ + price_unit + """, 0,""" + product_id+ """,""" + product_uom_qty + """, 1, 
                                                'manual', 0, 0, 0, 0, 
                                                0, 0, 2, 12, 1, 
                                                1, 'draft', 0, 2, NOW(), 
                                                2, NOW());"""

        try:
            self.cursor.execute(query_insert_sale_order_line)
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)