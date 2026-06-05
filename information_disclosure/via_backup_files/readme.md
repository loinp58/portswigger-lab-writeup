## Lab Description :

![image](https://github.com/sh3bu/Portswigger_labs/assets/67383098/f3c74200-20ed-4a5c-92ae-4056ab78b0f5)


## Solution :

Viết 1 tool bằng python để crawl các link và brute-force 1 vài path dựa trên worklist

The scan results reveal that there is a `/backup` directory.
![alt text](image.png)

#### /backup directory

![alt text](image-1.png)

Here we have a file named **ProductTemplate.java.bak**. Let's download the file & view its contents to retreive the **database password**

![alt text](image-2.png)

The above code uses **ConnectionBuilder class** to establish a connection to a *PostgreSQL* database. There we can see a random string [`vjghdou8bbwgpw7f0iha5av0diew9mrn`] which might be the database password that is used to establish the connection.

Submit the db_password to solve the lab.

![alt text](image-3.png)

## Result
![alt text](image-4.png)