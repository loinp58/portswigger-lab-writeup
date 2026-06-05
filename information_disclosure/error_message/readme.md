## Lab Description :

![image](https://github.com/sh3bu/Portswigger_labs/assets/67383098/e9606ff7-36e9-4366-9a19-1c31ed74e971)

## Solution :
GET request for product pages contains a productID parameter and send to Repeater


![alt text](image.png)

Change the value of the productId parameter to a non-integer data type, such as a string. Send the request:

```
GET /product?productId="example"
```

Response:
![alt text](image-1.png)

At the end of the response, we have the name & version of the software that is being used in the backend - `Apache Struts 2 2.3.31`

Go back to web and submit solution: ![alt text](image-2.png)

## Result
![alt text](image-3.png)