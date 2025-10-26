#!/usr/bin/env python3
"""
Script kiểm tra kết nối mạng cho Hit & Dodge P2P
Giúp debug vấn đề kết nối
"""
import socket
import sys

def get_local_ip():
    """Lấy IP address trong mạng LAN"""
    try:
        # Method 1: Connect to external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        try:
            # Method 2: Get hostname
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return None

def test_port(port=12345):
    """Kiểm tra xem port có mở được không"""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(('0.0.0.0', port))
        test_socket.close()
        return True, "OK"
    except Exception as e:
        return False, str(e)

def test_connection_to_host(host_ip, port=12345):
    """Kiểm tra kết nối đến host"""
    try:
        print(f"\n🔍 Đang kiểm tra kết nối đến {host_ip}:{port}...")
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(5)
        test_socket.connect((host_ip, port))
        test_socket.close()
        return True, "Kết nối thành công!"
    except socket.timeout:
        return False, "Timeout - Host không phản hồi"
    except ConnectionRefusedError:
        return False, "Connection refused - Host chưa mở server hoặc firewall đang chặn"
    except Exception as e:
        return False, f"Lỗi: {e}"

def main():
    print("=" * 60)
    print("HIT & DODGE - NETWORK DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    print(f"\n📡 IP Address của máy này: {local_ip}")
    
    if local_ip:
        if local_ip.startswith('127.'):
            print("⚠️  CẢNH BÁO: IP là localhost, có thể không kết nối được qua mạng")
            print("   Kiểm tra kết nối WiFi/LAN của bạn")
        else:
            print("✅ IP hợp lệ - Chia sẻ IP này với bạn bè để họ join")
    else:
        print("❌ Không thể lấy IP address")
    
    # Test port
    print(f"\n🔌 Kiểm tra port 12345...")
    can_bind, msg = test_port(12345)
    if can_bind:
        print(f"✅ Port 12345 sẵn sàng - Có thể tạo phòng host")
    else:
        print(f"❌ Port 12345 đang bận - {msg}")
        print("   Thử đóng các chương trình khác hoặc chờ vài giây")
    
    # Test connection to host (if provided)
    print("\n" + "=" * 60)
    test_host = input("\n🎮 Nhập IP của host để kiểm tra kết nối (Enter để bỏ qua): ").strip()
    
    if test_host:
        success, msg = test_connection_to_host(test_host, 12345)
        if success:
            print(f"✅ {msg}")
            print("   Bạn có thể join vào phòng của host này!")
        else:
            print(f"❌ {msg}")
            print("\n💡 Gợi ý khắc phục:")
            print("   1. Đảm bảo host đã chạy game và tạo phòng")
            print("   2. Kiểm tra cả 2 máy cùng mạng WiFi/LAN")
            print("   3. Tắt firewall tạm thời để test")
            print("   4. Thử ping IP của host: ping", test_host)
    
    print("\n" + "=" * 60)
    print("\n📝 HƯỚNG DẪN CHƠI:")
    print("   HOST:")
    print(f"   1. Chạy: python p2p_multiplayer.py")
    print(f"   2. Tạo phòng và chia sẻ IP: {local_ip}")
    print(f"   3. Chia sẻ mã phòng 4 ký tự")
    print()
    print("   CLIENT:")
    print(f"   1. Chạy: python p2p_multiplayer.py")
    print(f"   2. Nhập IP của host: {local_ip if local_ip else '[IP của host]'}")
    print(f"   3. Nhập mã phòng 4 ký tự")
    print(f"   4. Click THAM GIA")
    print()
    print("⚠️  LƯU Ý:")
    print("   - Tắt firewall nếu không kết nối được")
    print("   - Cả 2 máy phải cùng mạng WiFi/LAN")
    print("   - Port mặc định: 12345")
    print("=" * 60)

if __name__ == "__main__":
    main()
