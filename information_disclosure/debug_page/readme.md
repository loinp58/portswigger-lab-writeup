## Lab Description :

![image](https://github.com/sh3bu/Portswigger_labs/assets/67383098/817836d0-143c-4acd-8ab7-4cd55ab2c069)


## Solution :
Do không có bản Pro để làm như hướng dẫn, nên mò theo comment trong Elements của Dev tool, thấy có dòng như sau
```
<!-- <a href=/cgi-bin/phpinfo.php>Debug</a> -->
```
![alt text](image.png)

From that , we can see that there is a href pointing to **/cgi-bin/phpinfo.php**.

Send the request to repeater(add the path /cgi-bin/phpinfo.php)
![alt text](image-1.png)

n the response we can see that lot of information is revealed including the value of `SECRET_KEY` - `kb1yqb0ojgj6y1irx9bk9q3agutjrxpy`

```html
<tr>
  <td class="e">SECRET_KEY </td>
  <td class="v">kb1yqb0ojgj6y1irx9bk9q3agutjrxpy </td>
</tr>
```

Submit secret and done the lab
![alt text](image-2.png)

## Result
![alt text](image-3.png)