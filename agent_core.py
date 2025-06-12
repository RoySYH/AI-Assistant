import google.generativeai as genai
import json
from datetime import datetime
from typing import List, Dict, Any
import re
from tools.weather import WeatherTool
from tools.calendar import CalendarTool
from tools.email import EmailTool

class PersonalAssistant:
    """智能個人助理核心類"""
    
    def __init__(self, gemini_api_key: str, weather_api_key: str = None):
        """
        初始化助理
        
        Args:
            gemini_api_key: Google Gemini API 金鑰
            weather_api_key: 天氣API金鑰
        """
        # 配置 Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 初始化工具
        self.tools = {
            'weather': WeatherTool(weather_api_key) if weather_api_key else None,
            'calendar': CalendarTool(),
            'email': EmailTool()
        }
        
        # 系統提示詞
        self.system_prompt = """你是一個智能個人助理，名叫 AI助手。你的特點：

🎯 核心能力：
- 天氣查詢：可以查詢全球任何城市的即時天氣
- 日程管理：幫助用戶管理和安排日程
- 郵件處理：協助處理郵件相關任務
- 智能記憶：記住用戶的偏好和重要資訊

💬 對話風格：
- 友善、專業、有幫助
- 使用繁體中文回應
- 適當使用emoji讓對話更生動
- 主動提供建議和解決方案

🔧 工具使用：
- 當用戶詢問天氣時，使用天氣工具
- 當用戶需要安排日程時，使用日程工具
- 當用戶需要處理郵件時，使用郵件工具
- 根據上下文智能選擇合適的工具

📝 記憶運用：
- 參考用戶的歷史對話
- 記住用戶的偏好和習慣
- 提供個性化的建議

現在開始為用戶提供服務吧！"""

    def _detect_intent(self, user_input: str) -> Dict[str, Any]:
        """
        檢測用戶意圖
        
        Args:
            user_input: 用戶輸入
            
        Returns:
            包含意圖和參數的字典
        """
        user_input_lower = user_input.lower()
        
        # 天氣相關關鍵詞
        weather_keywords = ['天氣', '氣溫', '下雨', '晴天', '陰天', '風速', 'weather', 'temperature']
        # 日程相關關鍵詞  
        calendar_keywords = ['會議', '安排', '日程', '約會', '提醒', 'meeting', 'schedule', 'appointment']
        # 郵件相關關鍵詞
        email_keywords = ['郵件', '信件', '寄信', '回信', 'email', 'mail', 'send']
        
        intent = {
            'type': 'general',
            'confidence': 0.0,
            'entities': {}
        }
        
        # 檢測天氣意圖
        if any(keyword in user_input_lower for keyword in weather_keywords):
            intent['type'] = 'weather'
            intent['confidence'] = 0.8
            
            # 提取城市名稱
            cities = self._extract_cities(user_input)
            if cities:
                intent['entities']['city'] = cities[0]
        
        # 檢測日程意圖
        elif any(keyword in user_input_lower for keyword in calendar_keywords):
            intent['type'] = 'calendar'
            intent['confidence'] = 0.7
            
            # 提取時間資訊
            time_info = self._extract_time_info(user_input)
            if time_info:
                intent['entities'].update(time_info)
        
        # 檢測郵件意圖
        elif any(keyword in user_input_lower for keyword in email_keywords):
            intent['type'] = 'email'
            intent['confidence'] = 0.7
        
        return intent

    def _extract_cities(self, text: str) -> List[str]:
        """提取城市名稱"""
        # 常見城市列表
        cities = [
            '台北', '台中', '台南', '高雄', '桃園', '新竹', '台東', '花蓮',
            '台灣', '香港', '澳門', '北京', '上海', '廣州', '深圳',
            'taipei', 'taichung', 'kaohsiung', 'hong kong', 'macau',
            'beijing', 'shanghai', 'guangzhou', 'shenzhen',
            'tokyo', 'osaka', 'seoul', 'singapore', 'bangkok',
            'new york', 'london', 'paris', 'sydney', 'melbourne'
        ]
        
        found_cities = []
        text_lower = text.lower()
        
        for city in cities:
            if city.lower() in text_lower:
                found_cities.append(city)
        
        return found_cities

    def _extract_time_info(self, text: str) -> Dict[str, str]:
        """提取時間資訊"""
        time_info = {}
        
        # 時間關鍵詞
        if '今天' in text or '今日' in text:
            time_info['date'] = 'today'
        elif '明天' in text or '明日' in text:
            time_info['date'] = 'tomorrow'
        elif '後天' in text:
            time_info['date'] = 'day_after_tomorrow'
        
        # 提取具體時間
        time_patterns = [
            r'(\d{1,2})[點時]',
            r'(\d{1,2}):(\d{2})',
            r'(上午|下午|早上|晚上|中午)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            if matches:
                time_info['time'] = matches[0]
                break
        
        return time_info

    def _use_tool(self, tool_name: str, intent: Dict[str, Any], user_input: str) -> str:
        """
        使用指定工具
        
        Args:
            tool_name: 工具名稱
            intent: 用戶意圖
            user_input: 用戶輸入
            
        Returns:
            工具執行結果
        """
        if tool_name not in self.tools or not self.tools[tool_name]:
            return f"❌ {tool_name} 工具尚未配置"
        
        try:
            tool = self.tools[tool_name]
            
            if tool_name == 'weather':
                city = intent['entities'].get('city', '台北')
                return tool.get_weather(city)
            
            elif tool_name == 'calendar':
                return tool.manage_schedule(user_input, intent['entities'])
            
            elif tool_name == 'email':
                return tool.process_email(user_input)
            
        except Exception as e:
            return f"❌ 使用 {tool_name} 工具時發生錯誤: {str(e)}"
        
        return "❌ 工具執行失敗"

    def _generate_response(self, user_input: str, context: str, memories: List[str]) -> str:
        """
        生成回應
        
        Args:
            user_input: 用戶輸入
            context: 上下文資訊
            memories: 相關記憶
            
        Returns:
            生成的回應
        """
        # 構建提示詞
        prompt = f"""
基於以下資訊回應用戶：

用戶輸入：{user_input}

上下文資訊：
{context}

相關記憶：
{chr(10).join(memories) if memories else '無相關記憶'}

請生成一個有幫助、自然的回應。如果有使用工具獲得的資訊，請整合到回應中。
"""

        try:
            # 構建完整的提示詞
            full_prompt = f"""
{self.system_prompt}

基於以下資訊回應用戶：

用戶輸入：{user_input}

上下文資訊：
{context}

相關記憶：
{chr(10).join(memories) if memories else '無相關記憶'}

請生成一個有幫助、自然的回應。如果有使用工具獲得的資訊，請整合到回應中。
"""

            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"❌ 生成回應時發生錯誤: {str(e)}"

    def process_request(self, user_input: str, memories: List[str] = None, chat_history: List[Dict] = None) -> str:
        """
        處理用戶請求
        
        Args:
            user_input: 用戶輸入
            memories: 相關記憶
            chat_history: 聊天歷史
            
        Returns:
            助理回應
        """
        if not user_input.strip():
            return "請告訴我您需要什麼幫助 😊"
        
        # 檢測用戶意圖
        intent = self._detect_intent(user_input)
        
        # 初始化上下文
        context = f"當前時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # 根據意圖使用相應工具
        if intent['type'] != 'general' and intent['confidence'] > 0.5:
            tool_result = self._use_tool(intent['type'], intent, user_input)
            context += f"\n工具執行結果：\n{tool_result}\n"
        
        # 添加聊天歷史到上下文
        if chat_history:
            context += "\n最近對話：\n"
            for msg in chat_history[-3:]:  # 只取最近3條
                role = "用戶" if msg["role"] == "user" else "助理"
                context += f"{role}: {msg['content']}\n"
        
        # 生成最終回應
        response = self._generate_response(user_input, context, memories or [])
        
        return response

    def get_capabilities(self) -> Dict[str, bool]:
        """獲取助理能力狀態"""
        return {
            'weather': self.tools['weather'] is not None,
            'calendar': self.tools['calendar'] is not None,
            'email': self.tools['email'] is not None
        }