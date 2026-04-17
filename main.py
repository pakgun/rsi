import sys
import os
import datetime
import io
import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
import ta
import smtplib
from email.mime.text import MIMEText

class MarketAnalyzer:    
    def get_rsi(self, ticker, window=14):
        """RSI(14) 계산"""
        # auto_adjust=False 추가하여 FutureWarning 제거
        data = yf.download(ticker, period='3mo', interval='1d', progress=False, auto_adjust=False)
        rsi_indicator = ta.momentum.RSIIndicator(data['Close'].squeeze(), window=window)
        return round(rsi_indicator.rsi().iloc[-1], 2)

class MailUtil:
    def __init__(self):
        self.sender = "pakgun1513@gmail.com"
        self.recipients = ["nypark@kku.ac.kr"]
        self.password = os.getenv("EMAIL_PASSWORD")

    def send_email(self, subject, body):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(self.sender, self.password)
            smtp_server.sendmail(self.sender, self.recipients, msg.as_string())
        print("Message sent!")

def main():
    kst = datetime.timezone(datetime.timedelta(hours=9))
    now = datetime.datetime.now(kst)
    
    # 테스트를 위해 임시로 시간 조건문 주석 처리
    # if now.weekday() in (0, 1, 2, 3, 4) and 9 <= now.hour <= 16:
    print("프로그램 실행 시작...")
    analyzer = MarketAnalyzer()
    
    print("1/2. RSI 지표 수집 중...")
    rsi_result = {
        "KOSPI": analyzer.get_rsi('^KS11'),
        "KOSDAQ": analyzer.get_rsi('^KQ11'),
        "SP500": analyzer.get_rsi('^GSPC'),
        "NASDAQ": analyzer.get_rsi('^IXIC')
    }
    
    print("2/2. 조건 달성 여부 확인 및 이메일 발송 중...")
    if any(v <= 35 or v >= 65 for v in rsi_result.values()):
        
        # 지수별 마커 생성 함수
        def get_marker(rsi):
            if 0 <= rsi <= 30:
                return "🚨"
            elif 30 < rsi <= 35:
                return "⚠️"
            return ""
            
        k_name = f"{get_marker(rsi_result['KOSPI'])}KOSPI"
        kq_name = f"{get_marker(rsi_result['KOSDAQ'])}KOSDAQ"
        sp_name = f"{get_marker(rsi_result['SP500'])}S&P500"
        nd_name = f"{get_marker(rsi_result['NASDAQ'])}NASDAQ"

        # 이메일 제목용 한 줄 포맷
        subject = f"RSI [{k_name}: {rsi_result['KOSPI']}/{kq_name}: {rsi_result['KOSDAQ']}] [{sp_name}: {rsi_result['SP500']}/{nd_name}: {rsi_result['NASDAQ']}]"

        print("\n====================")
        print(f"발송될 제목: {subject}")
        print("====================\n")
        
        mail = MailUtil()
        mail.send_email(subject=subject, body="자동화된 RSI 지표 알림 메일입니다.")
    else:
        print("발송 조건에 부합하는 지수가 없어 메일을 발송하지 않습니다.")

    # Colab 테스트 시 오류 출력을 막기 위해 임시 주석 처리
    sys.exit()

if __name__ == "__main__":
    main()
