## Mô tả Lab
![alt text](image.png)

## Giải pháp

Vào form Feedback theo hướng dẫn. Điền dữ liệu vào form và submit.

Form feedback trông như sau
![alt text](image-1.png)

Request được bắt trong Burp Suite
![alt text](image-2.png)

Sửa tham số `email` thành
```
email=x||ping+-c+10+127.0.0.1||
```

## Kết quả
![alt text](image-3.png)

![alt text](image-4.png)