"""
主应用模块
整合所有后端组件，创建Flask应用
"""

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import logging
import threading
import time

from config import get_config
from api_routes import ProxyAPI
from websocket_handler import SocketIOHandler

class ProxyApp:
    """代理应用主类"""
    
    def __init__(self, config_name='development'):
        """
        初始化应用
        
        Args:
            config_name: 配置环境名称
        """
        self.config = get_config(config_name)
        self.app = None
        self.socketio = None
        self.proxy_api = None
        self.websocket_handler = None
        
        # 全局代理状态
        self.proxy_status = {
            'running': False,
            'port': self.config.DEFAULT_PROXY_PORT,
            'proxy_type': self.config.DEFAULT_PROXY_TYPE,
            'connections': 0,
            'total_bytes': 0,
            'active_connections': [],
            'start_time': None
        }
        
        self._setup_app()
        self._setup_logging()
    
    def _setup_app(self):
        """设置Flask应用"""
        self.app = Flask(__name__)
        self.app.config.from_object(self.config)
        
        # 配置CORS
        cors_config = self.config.get_cors_config()
        CORS(self.app, origins=cors_config['origins'])
        
        # 配置SocketIO
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins=cors_config['origins'],
            async_mode=self.config.SOCKETIO_ASYNC_MODE
        )
        
        # 初始化API和WebSocket处理器
        self.proxy_api = ProxyAPI(self.app, self.proxy_status, self.socketio)
        self.websocket_handler = SocketIOHandler(self.socketio, self.proxy_status)
        
        # 启动监控线程
        self._start_monitoring()
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Application initialized with {self.config.__class__.__name__}")
    
    def _start_monitoring(self):
        """启动监控线程"""
        def monitoring_loop():
            """监控循环"""
            while True:
                try:
                    # 更新代理状态
                    if self.proxy_api.proxy_server:
                        self.proxy_api.update_proxy_status()
                    
                    time.sleep(self.config.STATS_BROADCAST_INTERVAL)
                    
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(5)
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    def get_app(self):
        """获取Flask应用实例"""
        return self.app
    
    def get_socketio(self):
        """获取SocketIO实例"""
        return self.socketio
    
    def run(self, host='0.0.0.0', port=5000, debug=None):
        """
        运行应用
        
        Args:
            host: 监听地址
            port: 监听端口
            debug: 调试模式
        """
        if debug is None:
            debug = self.config.DEBUG
            
        logger = logging.getLogger(__name__)
        logger.info(f"Starting proxy application on {host}:{port}")
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug
        )

# 便捷函数
def create_app(config_name='development'):
    """
    创建应用工厂函数
    
    Args:
        config_name: 配置环境名称
        
    Returns:
        ProxyApp实例
    """
    return ProxyApp(config_name)

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True)
