# HƯỚNG DẪN CHƠI P2P MULTIPLAYER

## 🎮 Chơi 4 người trên 1 máy
```bash
python local_multiplayer.py
```

### Phím điều khiển:
- **Người 1 (Đỏ)**: Q (Hit), A (Dodge)
- **Người 2 (Xanh lá)**: W (Hit), S (Dodge)
- **Người 3 (Xanh dương)**: O (Hit), L (Dodge)
- **Người 4 (Vàng)**: P (Hit), ; (Dodge)

---

## 🌐 Chơi qua mạng LAN (4 máy khác nhau)

### Bước 1: Kiểm tra kết nối
```bash
python network_test.py
```
- Xem IP của bạn
- Kiểm tra port có sẵn sàng không
- Test kết nối nếu cần

### Bước 2: Người tạo phòng (1 người)
```bash
python p2p_multiplayer.py
```
1. Nhập tên
2. Click **"TẠO PHÒNG (HOST)"**
3. Nhớ **IP** và **mã phòng 4 ký tự**
4. Chia sẻ cho 3 người còn lại

**Ví dụ:**
- IP: `192.168.1.100`
- Mã phòng: `A3X9`

### Bước 3: Người tham gia (3 người)
```bash
python p2p_multiplayer.py
```
1. Nhập tên
2. Nhập IP của host: `192.168.1.100`
3. Nhập mã phòng: `A3X9`
4. Click **"THAM GIA"**

### Bước 4: Chơi!
- Game tự động bắt đầu khi đủ 4 người
- **SPACE/UP**: Hit (đánh bóng)
- **DOWN/ENTER**: Dodge (trốn)

---

## ❌ Không kết nối được?

### Checklist:
✅ **Cùng mạng WiFi/LAN**: Tất cả 4 máy phải kết nối cùng 1 mạng  
✅ **Tắt Firewall**: Tạm thời tắt firewall hoặc cho phép port 12345  
✅ **Host tạo phòng trước**: Host phải tạo phòng trước khi client join  
✅ **IP chính xác**: Nhập đúng IP (không phải 127.0.0.1)  
✅ **Mã phòng đúng**: Nhập đúng 4 ký tự mã phòng  

### Cách kiểm tra:

#### 1. Kiểm tra cùng mạng:
```bash
# Trên Linux/Mac
ping [IP_CUA_HOST]

# Ví dụ:
ping 192.168.1.100
```

#### 2. Kiểm tra firewall (Ubuntu/Linux):
```bash
# Tắt firewall tạm thời (để test)
sudo ufw disable

# Hoặc cho phép port 12345
sudo ufw allow 12345
```

#### 3. Kiểm tra port đang mở:
```bash
# Trên máy host
python network_test.py
```

#### 4. Xem log kết nối:
Khi chạy `p2p_multiplayer.py`, xem terminal có thông báo lỗi gì không.

---

## 💡 Tips

### Chơi qua Internet (không cùng WiFi):
Cần **Port Forwarding** trên router:
1. Vào router settings (thường là `192.168.1.1`)
2. Tìm **Port Forwarding** hoặc **Virtual Server**
3. Forward port `12345` đến IP của máy host
4. Dùng **IP public** (search "what is my ip" trên Google)
5. Client nhập IP public này

### Tối ưu kết nối:
- Dùng dây LAN thay vì WiFi cho ổn định hơn
- Đảm bảo bandwidth đủ (ít nhất 1 Mbps)
- Đóng các app tốn mạng khác

---

## 🐛 Debug

### Host không thấy IP:
```bash
# Xem tất cả IP
ip addr show  # Linux
ifconfig      # Mac
ipconfig      # Windows
```

### Client timeout:
- Host chưa mở game hoặc chưa tạo phòng
- Firewall đang chặn
- Không cùng mạng

### Disconnected giữa chừng:
- Mạng không ổn định
- Một trong 2 máy mất kết nối WiFi
- Firewall bật lại

---

## 📞 Hỗ trợ

Nếu vẫn gặp vấn đề:
1. Chạy `python network_test.py`
2. Chụp màn hình kết quả
3. Báo lỗi cụ thể trong terminal
