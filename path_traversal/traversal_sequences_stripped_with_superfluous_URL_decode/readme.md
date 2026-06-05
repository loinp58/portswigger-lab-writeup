## Mô tả Lab :
File path traversal, các chuỗi traversal bị loại bỏ với URL-decode dư thừa


![image](https://user-images.githubusercontent.com/67383098/235583370-5a684593-c018-4625-bb50-f1aaa0f38e45.png)


## Giải pháp :

Request tải ảnh trông như sau,

![image](1.png)

Trong lab này, server loại bỏ tất cả các chuỗi directory traversal **../** và cả **..%2F..%2F..%2F** (mã hóa kép), vì vậy để bypass chúng ta có thể dùng **mã hóa ba lần**.


Vì vậy để bypass, chúng ta dùng phiên bản mã hóa ba lần của **../../../etc/passwd** là `..%252F..%252F..%252Fetc%252Fpasswd` làm payload.

Lúc này chúng ta nhận được response chứa nội dung của file.

![image](image.png)


