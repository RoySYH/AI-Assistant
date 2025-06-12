import requests
from datetime import datetime
from typing import Dict, Optional

class WeatherTool:
    """天氣查詢工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化天氣工具
        
        Args:
            api_key: OpenWeatherMap API 金鑰
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # 城市名稱映射（中文到英文）
        self.city_mapping = {
            '台北': 'Taipei',
            '台中': 'Taichung', 
            '台南': 'Tainan',
            '高雄': 'Kaohsiung',
            '桃園': 'Taoyuan',
            '新竹': 'Hsinchu',
            '台東': 'Taitung',
            '花蓮': 'Hualien',
            '香港': 'Hong Kong',
            '澳門': 'Macau',
            '北京': 'Beijing',
            '上海': 'Shanghai',
            '廣州': 'Guangzhou',
            '深圳': 'Shenzhen',
            '東京': 'Tokyo',
            '大阪': 'Osaka',
            '首爾': 'Seoul',
            '新加坡': 'Singapore',
            '曼谷': 'Bangkok'
        }
        
        # 天氣狀況翻譯
        self.weather_translation = {
            'clear sky': '晴朗 ☀️',
            'few clouds': '少雲 🌤️',
            'scattered clouds': '多雲 ⛅',
            'broken clouds': '陰天 ☁️',
            'shower rain': '陣雨 🌦️',
            'rain': '下雨 🌧️',
            'thunderstorm': '雷雨 ⛈️',
            'snow': '下雪 ❄️',
            'mist': '薄霧 🌫️',
            'haze': '霾 😷',
            'fog': '霧 🌫️',
            'overcast clouds': '陰霾 ☁️'
        }
    
    def get_weather(self, city: str) -> str:
        """
        獲取指定城市的天氣資訊
        
        Args:
            city: 城市名稱
            
        Returns:
            格式化的天氣資訊字符串
        """
        if not self.api_key:
            return self._get_mock_weather(city)
        
        try:
            # 處理城市名稱
            city_en = self.city_mapping.get(city, city)
            
            # 構建API請求
            params = {
                'q': city_en,
                'appid': self.api_key,
                'units': 'metric',  # 使用攝氏度
                'lang': 'zh_tw'  # 繁體中文
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_weather_response(data, city)
            elif response.status_code == 404:
                return f"❌ 找不到城市「{city}」的天氣資訊"
            else:
                return f"❌ 無法獲取天氣資訊，API 返回錯誤: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "❌ 天氣API請求超時，請稍後再試"
        except requests.exceptions.RequestException as e:
            return f"❌ 網路連接錯誤: {str(e)}"
        except Exception as e:
            return f"❌ 獲取天氣資訊時發生錯誤: {str(e)}"
    
    def _format_weather_response(self, data: Dict, city: str) -> str:
        """
        格式化天氣回應
        
        Args:
            data: API 返回的天氣資料
            city: 城市名稱
            
        Returns:
            格式化的天氣資訊
        """
        try:
            # 提取關鍵資訊
            main = data['main']
            weather = data['weather'][0]
            wind = data.get('wind', {})
            
            temperature = round(main['temp'])
            feels_like = round(main['feels_like'])
            humidity = main['humidity']
            pressure = main['pressure']
            
            # 翻譯天氣狀況
            weather_desc = weather['description']
            weather_main = weather['main'].lower()
            translated_weather = self.weather_translation.get(
                weather_desc.lower(), 
                self._translate_weather_condition(weather_main)
            )
            
            # 風速資訊
            wind_speed = wind.get('speed', 0)
            wind_info = f"{wind_speed:.1f} m/s" if wind_speed > 0 else "無風"
            
            # 構建回應
            weather_report = f"""🌤️ **{city} 天氣資訊**

🌡️ **溫度**: {temperature}°C (體感 {feels_like}°C)
☁️ **天氣**: {translated_weather}
💧 **濕度**: {humidity}%
🌬️ **風速**: {wind_info}
📊 **氣壓**: {pressure} hPa

📅 **更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

{self._get_weather_advice(temperature, weather_main, humidity)}"""
            
            return weather_report
            
        except KeyError as e:
            return f"❌ 解析天氣資料時發生錯誤，缺少欄位: {e}"
        except Exception as e:
            return f"❌ 格式化天氣資訊時發生錯誤: {str(e)}"
    
    def _translate_weather_condition(self, condition: str) -> str:
        """翻譯天氣狀況"""
        conditions = {
            'clear': '晴朗 ☀️',
            'clouds': '多雲 ☁️',
            'rain': '下雨 🌧️',
            'drizzle': '毛毛雨 🌦️',
            'thunderstorm': '雷雨 ⛈️',
            'snow': '下雪 ❄️',
            'mist': '薄霧 🌫️',
            'fog': '霧 🌫️',
            'haze': '霾 😷',
            'dust': '沙塵 🌪️',
            'sand': '沙暴 🌪️',
            'ash': '火山灰 🌋',
            'squall': '颮風 💨',
            'tornado': '龍捲風 🌪️'
        }
        
        return conditions.get(condition.lower(), f'{condition} 🌤️')
    
    def _get_weather_advice(self, temperature: int, condition: str, humidity: int) -> str:
        """根據天氣狀況提供建議"""
        advice = "💡 **貼心提醒**: "
        
        # 溫度建議
        if temperature < 10:
            advice += "氣溫較低，記得多穿衣保暖！"
        elif temperature > 30:
            advice += "氣溫較高，注意防曬和補水！"
        elif 15 <= temperature <= 25:
            advice += "氣溫舒適，是外出的好天氣！"
        
        # 天氣狀況建議
        if 'rain' in condition.lower() or 'drizzle' in condition.lower():
            advice += " 記得帶雨具！"
        elif 'thunderstorm' in condition.lower():
            advice += " 有雷雨，避免戶外活動！"
        elif 'snow' in condition.lower():
            advice += " 路面可能濕滑，注意安全！"
        
        # 濕度建議
        if humidity > 80:
            advice += " 濕度較高，可能會感覺悶熱。"
        elif humidity < 30:
            advice += " 濕度較低，記得補充水分。"
        
        return advice
    
    def _get_mock_weather(self, city: str) -> str:
        """
        當沒有API金鑰時提供模擬天氣資訊
        
        Args:
            city: 城市名稱
            
        Returns:
            模擬的天氣資訊
        """
        import random
        
        # 模擬天氣資料
        mock_temps = [18, 22, 25, 28, 15, 20, 24, 26]
        mock_conditions = [
            ('晴朗 ☀️', 'clear'),
            ('多雲 ☁️', 'cloudy'), 
            ('小雨 🌧️', 'rain'),
            ('陰天 ⛅', 'overcast')
        ]
        
        temp = random.choice(mock_temps)
        condition, condition_en = random.choice(mock_conditions) 
        humidity = random.randint(45, 85)
        
        return f"""🌤️ **{city} 天氣資訊** (模擬資料)

🌡️ **溫度**: {temp}°C
☁️ **天氣**: {condition}
💧 **濕度**: {humidity}%
📅 **更新時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

⚠️ **注意**: 這是模擬資料，請在側邊欄配置 Weather API Key 以獲得真實天氣資訊。

💡 如何獲取免費API金鑰：
1. 訪問 https://openweathermap.org/api
2. 註冊免費帳戶
3. 獲取 API Key 並在側邊欄輸入

{self._get_weather_advice(temp, condition_en, humidity)}"""
    
    def get_forecast(self, city: str, days: int = 5) -> str:
        """
        獲取天氣預報（需要付費API）
        
        Args:
            city: 城市名稱
            days: 預報天數
            
        Returns:
            天氣預報資訊
        """
        return f"📅 **{city} {days}天天氣預報**\n\n⚠️ 此功能需要升級API方案，目前僅提供當日天氣查詢。"