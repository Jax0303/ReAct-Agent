"""
설정 관리 유틸리티
Configuration Management Utility
"""
import os
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class Config:
    """설정 클래스"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    # 워크플로우 설정
    DEFAULT_MAX_ITERATIONS = int(os.getenv("DEFAULT_MAX_ITERATIONS", "3"))
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
    
    # 도구 설정
    DEFAULT_MAX_RETRIES = int(os.getenv("DEFAULT_MAX_RETRIES", "3"))
    DEFAULT_NEWS_RESULTS = int(os.getenv("DEFAULT_NEWS_RESULTS", "5"))
    
    @classmethod
    def validate_config(cls) -> bool:
        """설정 유효성 검증"""
        # OpenAI 또는 Google AI API 키 중 하나는 필요
        has_openai = bool(cls.OPENAI_API_KEY)
        has_google_ai = bool(cls.GOOGLE_AI_API_KEY)
        
        if not (has_openai or has_google_ai):
            logger.error("OPENAI_API_KEY 또는 GOOGLE_AI_API_KEY 중 하나는 필요합니다.")
            return False
        
        logger.info("설정 유효성 검증 완료")
        return True
    
    @classmethod
    def get_openai_client_config(cls) -> dict:
        """OpenAI 클라이언트 설정 반환"""
        return {
            "api_key": cls.OPENAI_API_KEY,
            "timeout": cls.DEFAULT_TIMEOUT
        }
