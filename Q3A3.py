import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np


def connect(path):
    global connection
    global connection
    global cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    return


    
def uninformed():
    cursor.execute(' PRAGMA automatic_index = OFF; ')

    cursor.execute('DROP TABLE IF EXISTS customer1')
    cursor.execute('DROP TABLE IF EXISTS Orders1')
    cursor.execute('DROP TABLE IF EXISTS Oid') 
    cursor.execute('DROP TABLE IF EXISTS temp')
    cursor.execute('DROP TABLE IF EXISTS temp1')
    cursor.execute('DROP TABLE IF EXISTS temp2')
    
    cursor.execute('CREATE TABLE Customer1 (customer_id Text, customer_postal_code INTEGER);')
    cursor.execute('INSERT INTO Customer1 SELECT customer_id, customer_postal_code FROM Customers')
    cursor.execute('ALTER TABLE Customers RENAME TO temp; ')
    cursor.execute('ALTER TABLE Customer1 RENAME TO Customers; ')
    
    cursor.execute('CREATE TABLE Orders1 (order_id Text, customer_id TEXT);')
    cursor.execute('INSERT INTO Orders1 SELECT order_id, customer_id FROM Orders')
    cursor.execute('ALTER TABLE Orders RENAME TO temp1; ')
    cursor.execute('ALTER TABLE Orders1 RENAME TO Orders; ')

    cursor.execute('CREATE TABLE Oid (order_id	TEXT,order_item_id INTEGER, product_id TEXT, seller_id TEXT);')
    cursor.execute('INSERT INTO Oid SELECT order_id, order_item_id,product_id, seller_id FROM Order_items')
    cursor.execute('ALTER TABLE Order_items RENAME TO temp2; ')
    cursor.execute('ALTER TABLE Oid RENAME TO Order_items')


    
    connection.commit()



def Self_optimized():
    cursor.execute(' PRAGMA automatic_index = ON; ')

    cursor.execute('DROP TABLE Customers; ')
    cursor.execute('ALTER TABLE temp RENAME TO Customers; ')

    cursor.execute('DROP TABLE Orders; ')
    cursor.execute('ALTER TABLE temp1 RENAME TO Orders; ')

    cursor.execute('DROP TABLE Order_items; ')
    cursor.execute('ALTER TABLE temp2 RENAME TO Order_items; ')
    connection.commit()




def User_optimized():
    cursor.execute(' PRAGMA automatic_index = ON;')

    cursor.execute('DROP INDEX IF EXISTS Orders_customer_id_ix;')
    cursor.execute('DROP INDEX IF EXISTS Order_items_order_id_ix;')
    cursor.execute('DROP INDEX IF EXISTS Cutomers_customer_postal_code_ix;')
    cursor.execute('DROP INDEX IF EXISTS Customers_customer_id_ix ;')

    cursor.execute('CREATE INDEX Cutomers_customer_postal_code_ix ON Customers(customer_postal_code);')    
    cursor.execute(' CREATE INDEX Orders_customer_id_ix ON Orders(customer_id);')
    cursor.execute(' CREATE INDEX Customers_customer_id_ix ON Customers(customer_id);')
    cursor.execute(' CREATE INDEX Order_items_order_id_ix ON Order_items(order_id);')
    
    connection.commit()


def query(pc):

    query =('''Select count(a.oid), Avg(a.size)
            From Customers c, Orders o
            Left Outer Join (Select order_id as oid, count(order_item_id) as size
                From Order_items
                Group By Order_items.order_id) as a On o.order_id = a.oid
    Where c.customer_postal_code = :P and c.customer_id = o.customer_id''')



    cursor.execute(query,{'P':pc})
    connection.commit()

    

def runtime(PostCodes):

    stime = time.time()
    for i in PostCodes:
        query(i)
    qtime = time.time()*1000 - stime*1000
    print(" %s milliseconds " % (qtime))
    return qtime

def RunDB(DBname):
    case = ['uni', 'self', 'user']
    T = []

    connect(DBname)
    cursor.execute('''Select distinct customer_postal_code
                   From Customers
                   order by random() limit 50''')

    PostCodes= []
    rows = cursor.fetchall()
    for i in rows:
        PostCodes.append(i[0])
    connection.commit()

    for i in case:
        if i == 'uni':
            uninformed()
            T.append(runtime(PostCodes))
        elif i == 'self':
            Self_optimized()
            T.append(runtime(PostCodes))
        else:
            User_optimized()
            T.append(runtime(PostCodes))
            cursor.execute('DROP INDEX Orders_customer_id_ix;')
            cursor.execute('DROP INDEX Order_items_order_id_ix;')
            cursor.execute('DROP INDEX Cutomers_customer_postal_code_ix;')
            cursor.execute('DROP INDEX Customers_customer_id_ix;')
            connection.commit()

    connection.close()
    return T


def bar_chart(DBsmall,DBmedium,DBlarge):
    labels = ['SmallDB', 'MediumDB', 'LargeDB']

    uninformed = [DBsmall[0], DBmedium[0], DBlarge[0]]
    self_optimized = [DBsmall[1], DBmedium[1], DBlarge[1]]
    user_optimized = [DBsmall[2], DBmedium[2], DBlarge[2]]

    width = 0.65       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    b_User= list(np.add(uninformed,self_optimized))

    ax.bar(labels, uninformed, width, label='Uninformed')
    ax.bar(labels, self_optimized, width, bottom=uninformed, label='Self-optimized')
    ax.bar(labels, user_optimized, width, bottom=b_User, label='User-optimized')


    #ax.set_ylabel('ms')
    ax.set_title('Query 3 (runtime in ms)')
    ax.legend()
    plt.show()
    
    
    return


def main():

    #running different database sizes

    DBs = RunDB('./A3small.db')

    DBm = RunDB('./A3Medium.db')

    DBl = RunDB('./A3Large.db')

    # make bar chart
    bar_chart(DBs,DBm,DBl)

    
    
if __name__ == "__main__":
    main()
