import logging
import sys
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler
from contextvars import ContextVar
import uuid

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        msg = str(record.msg)
        # Basic mask for tokens and keys
        msg = re.sub(r'(Bearer\s+)[a-zA-Z0-9\-\._~+/]+=*', r'\1***', msg)
        msg = re.sub(r'(api_key=)[a-zA-Z0-9\-\._~+/]+=*', r'\1***', msg)
        msg = re.sub(r'("password":\s*")[^"]+(")', r'\1***\2', msg)
        record.msg = msg
        return True

class CustomFormatter(logging.Formatter):
    def format(self, record):
        latency = getattr(record, 'latency', '-')
        provider = getattr(record, 'provider', '-')
        retry = getattr(record, 'retry', '-')
        status = getattr(record, 'status', '-')
        
        if isinstance(latency, float):
            latency = f"{latency:.2f}s"
            
        record.latency_str = latency
        record.provider_str = provider
        record.retry_str = retry
        record.status_str = status
        record.request_id = request_id_ctx.get()
        record.correlation_id = correlation_id_ctx.get()
        return super().format(record)

def setup_logger():
    # Sadece bir kere configure etmek icin
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.setLevel(logging.INFO)
    
    formatter = CustomFormatter(
        fmt="%(asctime)s [%(levelname)s] [Req:%(request_id)s] [Corr:%(correlation_id)s] %(name)s | Latency:%(latency_str)s | Provider:%(provider_str)s | Retry:%(retry_str)s | Status:%(status_str)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    
    # 10MB per file, max 5 files
    file_handler = RotatingFileHandler(
        LOG_DIR / "lingofy.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SensitiveDataFilter())
    
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

setup_logger()

def get_logger(name: str):
    return logging.getLogger(name)
