## Lab description
![alt text](image.png)

## Solution
Thử truy cập vào path `/admin`, bị **"Access denied"**

Request truy cập `/` đẩy vào Repeater, bổ sung thêm header `X-Original-Url: /invalid` thì response trả về `Not Found`
![alt text](image-1.png)

Có thể là Backend sẽ xử lý URL thông qua header này
Thay giá trị `/admin` vào header trên, ta sẽ truy cập được vào admin panel
![alt text](image-2.png)

Path để delete user `carlos` là `/admin/delete?username=carlos`
Ta thay `X-Original-Url: /admin/delete` và để parameter trên url
![alt text](image-3.png)

Như vậy là account `carlos` đã bị xóa

## Result
![alt text](image-4.png)