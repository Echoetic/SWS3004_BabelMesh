"""
代理服务器核心模块
实现HTTP和SOCKS5代理服务器功能
"""

import socket
import threading
import select
import ssl
import logging
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class ProxyServer:
    """
    代理服务器类，支持HTTP和SOCKS5协议
    """
    
    def __init__(self, host='0.0.0.0', port=8888, proxy_type='http'):
        """
        初始化代理服务器
        
        Args:
            host (str): 监听地址
            port (int): 监听端口
            proxy_type (str): 代理类型 ('http' 或 'socks5')
        """
        self.host = host
        self.port = port
        self.proxy_type = proxy_type  # 'http' 或 'socks5'
        self.server_socket = None
        self.running = False
        self.connections = {}
        
    def start(self):
        """启动代理服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"{self.proxy_type.upper()} proxy server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_sock, addr = self.server_socket.accept()
                    connection_id = f"{addr[0]}:{addr[1]}"
                    self.connections[connection_id] = {
                        'start_time': datetime.now(),
                        'bytes_sent': 0,
                        'bytes_received': 0,
                        'target': None
                    }
                    
                    thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_sock, addr, connection_id),
                        daemon=True
                    )
                    thread.start()
                    
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connections: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start proxy server: {e}")
            raise
    
    def stop(self):
        """停止代理服务器"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info(f"{self.proxy_type.upper()} proxy server stopped")
        
    def handle_client(self, client_sock, addr, connection_id):
        """
        处理客户端连接
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
        try:
            if self.proxy_type == 'http':
                self.handle_http_proxy(client_sock, addr, connection_id)
            else:
                self.handle_socks5_proxy(client_sock, addr, connection_id)
        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            client_sock.close()
            
            # 清理连接记录
            if connection_id in self.connections:
                del self.connections[connection_id]
    
    def handle_http_proxy(self, client_sock, addr, connection_id):
        """
        处理HTTP代理请求
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
        remote = None
        try:
            # 读取HTTP请求
            request = b''
            while b'\r\n\r\n' not in request:
                chunk = client_sock.recv(4096)
                if not chunk:
                    return
                request += chunk
            
            # 解析HTTP请求
            request_line = request.split(b'\r\n')[0].decode('utf-8')
            method, url, version = request_line.split(' ')
            
            if method == 'CONNECT':
                # HTTPS连接 (CONNECT方法)
                host, port = url.split(':')
                port = int(port)
                
                # 连接目标服务器
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.settimeout(10)
                remote.connect((host, port))
                
                # 更新连接信息
                self.connections[connection_id]['target'] = f"{host}:{port}"
                
                # 回复连接建立成功
                client_sock.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
                
                # 开始数据转发
                self.forward_data(client_sock, remote, connection_id)
                
            else:
                # HTTP请求 (GET, POST等)
                if url.startswith('http://'):
                    # 解析URL
                    parsed = urlparse(url)
                    host = parsed.hostname
                    port = parsed.port or 80
                    path = parsed.path or '/'
                    if parsed.query:
                        path += '?' + parsed.query
                else:
                    # 相对URL，从Host头获取
                    host_header = None
                    for line in request.split(b'\r\n')[1:]:
                        if line.startswith(b'Host: '):
                            host_header = line[6:].decode('utf-8')
                            break
                    
                    if host_header:
                        host = host_header
                        port = 80
                        path = url
                    else:
                        client_sock.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')
                        return
                
                # 连接目标服务器
                remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                remote.settimeout(10)
                remote.connect((host, port))
                
                # 更新连接信息
                self.connections[connection_id]['target'] = f"{host}:{port}"
                
                # 修改请求为相对路径并转发
                modified_request = request.replace(url.encode(), path.encode())
                remote.sendall(modified_request)
                
                # 开始数据转发
                self.forward_data(client_sock, remote, connection_id)
                
        except Exception as e:
            logger.error(f"HTTP proxy error: {e}")
            try:
                client_sock.sendall(b'HTTP/1.1 502 Bad Gateway\r\n\r\n')
            except:
                pass
        finally:
            if remote:
                remote.close()
    
    def handle_socks5_proxy(self, client_sock, addr, connection_id):
        """
        处理SOCKS5代理请求
        
        Args:
            client_sock: 客户端socket
            addr: 客户端地址
            connection_id: 连接ID
        """
        remote = None
        try:
            # SOCKS5 握手
            ver, nmethods = client_sock.recv(2)
            methods = client_sock.recv(nmethods)
            client_sock.sendall(b'\x05\x00')  # 无认证
            
            # 请求阶段
            ver, cmd, _, atyp = client_sock.recv(4)
            
            if atyp == 1:  # IPv4
                addr_bytes = client_sock.recv(4)
                target_addr = socket.inet_ntoa(addr_bytes)
            elif atyp == 3:  # 域名
                domain_len = client_sock.recv(1)[0]
                target_addr = client_sock.recv(domain_len).decode()
            else:
                client_sock.close()
                return
                
            port = int.from_bytes(client_sock.recv(2), 'big')
            
            if cmd != 1:  # 只支持CONNECT
                client_sock.close()
                return
                
            # 连接目标服务器
            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.settimeout(10)
            remote.connect((target_addr, port))
            
            # 更新连接信息
            self.connections[connection_id]['target'] = f"{target_addr}:{port}"
            
            # 回复成功
            reply = b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + (8888).to_bytes(2, 'big')
            client_sock.sendall(reply)
            
            # 开始数据转发
            self.forward_data(client_sock, remote, connection_id)
            
        except Exception as e:
            logger.error(f"SOCKS5 proxy error: {e}")
        finally:
            if remote:
                remote.close()
    
    def forward_data(self, client_sock, remote, connection_id):
        """
        数据转发函数 - 实现实时流量监控
        
        Args:
            client_sock: 客户端socket
            remote: 远程服务器socket  
            connection_id: 连接ID
        """
        sockets = [client_sock, remote]
        while self.running:
            try:
                r, _, _ = select.select(sockets, [], [], 1.0)
                for s in r:
                    data = s.recv(4096)
                    if not data:
                        return
                        
                    if s is client_sock:
                        # 客户端到服务器的数据
                        remote.sendall(data)
                        self.connections[connection_id]['bytes_sent'] += len(data)
                    else:
                        # 服务器到客户端的数据
                        client_sock.sendall(data)
                        self.connections[connection_id]['bytes_received'] += len(data)
                        
            except Exception as e:
                logger.error(f"Error in data forwarding: {e}")
                break
    
    def get_connections_stats(self):
        """获取连接统计信息"""
        total_bytes = 0
        active_connections = []
        
        for conn_id, info in self.connections.items():
            total_bytes += info['bytes_sent'] + info['bytes_received']
            active_connections.append({
                'id': conn_id,
                'target': info['target'],
                'bytes_sent': info['bytes_sent'],
                'bytes_received': info['bytes_received'],
                'start_time': info['start_time'].isoformat()
            })
        
        return {
            'total_connections': len(self.connections),
            'total_bytes': total_bytes,
            'active_connections': active_connections
        }
