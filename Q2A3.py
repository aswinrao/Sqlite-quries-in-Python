import sqlite3
import time
import matplotlib.pyplot as plt
import numpy as np

connection = None
cursor = None

def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    connection.commit()
    return

def uninformed():
    cursor.execute(' PRAGMA automatic_index=OFF; ')

    cursor.execute('''CREATE TABLE Customer1 (customer_id Text, customer_postal_code INTEGER);''')
    cursor.execute('''INSERT INTO Customer1 SELECT customer_id, customer_postal_code FROM Customers''')
    cursor.execute('''ALTER TABLE Customers RENAME TO temp; ''')
    cursor.execute('''ALTER TABLE Customer1 RENAME TO Customers; ''')
    
    cursor.execute('''CREATE TABLE Orders1 (order_id Text, customer_id TEXT);''')
    cursor.execute('''INSERT INTO Orders1 SELECT order_id, customer_id FROM Orders''')
    cursor.execute('''ALTER TABLE Orders RENAME TO temp1; ''')
    cursor.execute('''ALTER TABLE Orders1 RENAME TO Orders; ''')

    connection.commit()



def Self_optimized():
    cursor.execute(' PRAGMA automatic_index=ON; ')

    cursor.execute('''DROP TABLE Customers; ''')
    cursor.execute('''ALTER TABLE temp RENAME TO Customers; ''')

    cursor.execute('''DROP TABLE Orders; ''')
    cursor.execute('''ALTER TABLE temp1 RENAME TO Orders; ''')
    connection.commit()




def User_optimized():
    cursor.execute(' PRAGMA automatic_index=ON; ')
    cursor.execute(' CREATE INDEX Orders_customer_id_ix ON Orders(customer_id);')
    cursor.execute(' CREATE INDEX Customers_customer_id_ix ON Customers(customer_id);')
    cursor.execute('CREATE INDEX Cutomers_customer_postal_code_ix ON Customers(customer_postal_code);')
    connection.commit()

    



def query(x):
    global connection, cursor
    

    query =('''Select Avg(v.size)
    From Orders o, Customers c
    LEFT OUTER JOIN OrderSize v
    ON o.order_id = v.oid
    Where c.customer_id=o.customer_id 
    and c.customer_postal_code =:P''')


    cursor.execute(query,{'P':x})
    connection.commit()

    





def bar_chart(UnStime1,SStime2,UsStime3,UnMtime1,SMtime2,UsMtime3,UnLtime1,SLtime2,UsLtime3):
    labels = ['SmallDB', 'MediumDB', 'LargeDB']

    uninformed = [UnStime1, UnMtime1, UnLtime1]
    self_optimized = [SStime2, SMtime2, SLtime2]
    user_optimized = [UsStime3, UsMtime3, UsLtime3]

    width = 0.65       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    b_User= list(np.add(uninformed,self_optimized))

    ax.bar(labels, uninformed, width, label='Uninformed')
    ax.bar(labels, self_optimized, width, bottom=uninformed, label='Self-optimized')
    ax.bar(labels, user_optimized, width, bottom=b_User, label='User-optimized')


    #ax.set_ylabel('ms')
    ax.set_title('Query 2 (runtime in ms)')
    ax.legend()

    plt.show()
    return


def main():
    #Connect the A3Small.db
    global connection
    connect('./A3small.db')


    view = ('''Create view OrderSize 
    as
    SELECT order_id as oid, Count(order_item_id) as size 
    From Order_items
    group by order_id ''')

    cursor.execute(view)
    cursor.execute('''select distinct customer_postal_code from customers order by random() limit 50''')


    RandList= []
    rows = cursor.fetchall()
    for row in rows:
        RandList.append(row[0])
    connection.commit()


    #Get the Uninformed scenario in A3small
    num = 1
    i=0
    uninformed()
    start_time = time.time()
    while num <51:
        query(RandList[i])
        i=i+1
        num = num+1
    UnStime1 = time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UnStime1))
    connection.close()


    #Get the Self_optimized scenario in A3small
    connect('./A3small.db')
    num2 = 1
    j=0
    Self_optimized()
    start_time = time.time()
    while num2 <51:
        query(RandList[j])
        j=j+1
        num2 = num2+1
    SStime2=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (SStime2))
    connection.close()


    #Get the User_optimized scenario in A3small
    connect('./A3small.db')
    num3 = 1
    k=0
    User_optimized()
    start_time = time.time()
    while num3 <51:
        query(RandList[k])
        num3 = num3+1
    UsStime3=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UsStime3))
    cursor.execute('DROP INDEX Orders_customer_id_ix;')
    cursor.execute('DROP INDEX Cutomers_customer_postal_code_ix;')
    cursor.execute('DROP INDEX Customers_customer_id_ix ;')
    cursor.execute('''DROP view OrderSize''')
    connection.commit()
    connection.close()


    #Connect the A3Medium.db and create a view
    connect('./A3Medium.db')
    view = ('''Create view OrderSize 
    as
    SELECT order_id as oid, Count(order_item_id) as size 
    From Order_items
    group by order_id ''')
    cursor.execute(view)


    #Ceate RandList contains 50 distinct postal codes in A3Medium in a list
    cursor.execute('''select distinct customer_postal_code from customers order by random() limit 50''')
    RandList= []
    rows = cursor.fetchall()
    for row in rows:
        RandList.append(row[0])
    connection.commit()


    #Get the Uninformed scenario in A3medium
    num = 1
    i=0
    uninformed()
    start_time = time.time()
    while num <51:
        query(RandList[i])
        i=i+1
        num = num+1
    UnMtime1 = time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UnMtime1))
    connection.close()


    #Get the Self_optimized scenario in A3Medium
    connect('./A3Medium.db')
    num2 = 1
    j=0
    Self_optimized()
    start_time = time.time()
    while num2 <51:
        query(RandList[j])
        j=j+1
        num2 = num2+1
    SMtime2=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (SMtime2))
    connection.close()


    #Get the User_optimized scenario in A3Medium
    connect('./A3Medium.db')
    num3 = 1
    k=0
    User_optimized()
    start_time = time.time()
    while num3 <51:
        query(RandList[k])
        num3 = num3+1
    UsMtime3=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UsMtime3))

    # drop index and view 
    cursor.execute('DROP INDEX Orders_customer_id_ix;')
    cursor.execute('DROP INDEX Cutomers_customer_postal_code_ix;')
    cursor.execute('DROP INDEX Customers_customer_id_ix ;')
    cursor.execute('''DROP view OrderSize''')    
    connection.commit()
    connection.close()


    #Connect the A3Large.db and create a view
    connect('./A3Large.db')
    view = ('''Create view OrderSize 
    as
    SELECT order_id as oid, Count(order_item_id) as size 
    From Order_items
    group by order_id ''')
    cursor.execute(view)


    #Ceate RandList contains 50 distinct postal codes in A3Large in a list
    cursor.execute('''select distinct customer_postal_code from customers order by random() limit 50''')
    RandList= []
    rows = cursor.fetchall()
    for row in rows:
        RandList.append(row[0])
    connection.commit()


    #Get the Uninformed scenario in A3Large
    num = 1
    i=0
    uninformed()
    start_time = time.time()
    while num <51:
        query(RandList[i])
        i=i+1
        num = num+1
    UnLtime1 = time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UnLtime1))
    connection.close()


    #Get the Self_optimized scenario in A3Large
    connect('./A3Large.db')
    num2 = 1
    j=0
    Self_optimized()
    start_time = time.time()
    while num2 <51:
        query(RandList[j])
        j=j+1
        num2 = num2+1
    SLtime2=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (SLtime2))
    connection.close()


    #Get the User_optimized scenario in A3Large
    connect('./A3Large.db')
    num3 = 1
    k=0
    User_optimized()
    start_time = time.time()
    while num3 <51:
        query(RandList[k])
        num3 = num3+1
    UsLtime3=time.time()*1000 - start_time*1000
    print(" %s milliseconds " % (UsLtime3))


    # drop index and view 
    cursor.execute('DROP INDEX Orders_customer_id_ix;')
    cursor.execute('DROP INDEX Cutomers_customer_postal_code_ix;')
    cursor.execute('DROP INDEX Customers_customer_id_ix ;')
    cursor.execute('''DROP view OrderSize''')
    connection.commit()
    connection.close()


    # make bar chart
    bar_chart(UnStime1,SStime2,UsStime3,UnMtime1,SMtime2,UsMtime3,UnLtime1,SLtime2,UsLtime3)

    
    
if __name__ == "__main__":
    main()
