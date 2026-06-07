## Lab Description :

![alt text](image.png)


## Solution :

Access to admin page via path `/admin`
![alt text](image-2.png)

Clicking on `My account` takes us to a login page.

![alt text](image-1.png)

We enter the credentials which is given in the lab description - `wiener:peter`

When we login we get to see
![alt text](image-3.png)

Response đã set 2 Cookie là session để lưu phiên đăng nhập và 1 cookie là Admin=false để đánh dấu `wiener` không phải admin. 

Vào Application trên dev-tool, sửa cookie `Admin=true`, page sẽ hiện ra Admin Panel
![alt text](image-4.png)

Truy cập vào Admin Panel và xóa user `carlos` là đã hoàn thành bài
![alt text](image-5.png)

## Result
![alt text](image-6.png)
