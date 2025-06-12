from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import re

class CalendarTool:
    """日程管理工具"""
    
    def __init__(self):
        """初始化日程管理工具"""
        # 在實際應用中，這裡會連接到真實的日程數據庫
        # 現在我們使用內存存儲作為演示
        self.events = []
        self.event_id_counter = 1
    
    def manage_schedule(self, user_input: str, entities: Dict[str, Any]) -> str:
        """
        管理日程安排
        
        Args:
            user_input: 用戶輸入
            entities: 提取的實體信息
            
        Returns:
            處理結果
        """
        # 檢測用戶意圖
        intent = self._detect_schedule_intent(user_input)
        
        if intent == 'add':
            return self._add_event(user_input, entities)
        elif intent == 'view':
            return self._view_events(entities)
        elif intent == 'delete':
            return self._delete_event(user_input)
        elif intent == 'update':
            return self._update_event(user_input, entities)
        else:
            return self._provide_schedule_help()
    
    def _detect_schedule_intent(self, user_input: str) -> str:
        """檢測日程管理意圖"""
        user_input_lower = user_input.lower()
        
        # 添加事件關鍵詞
        add_keywords = ['安排', '預約', '設定', '新增', '添加', '約', '會議', 'schedule', 'add', 'book']
        # 查看事件關鍵詞
        view_keywords = ['查看', '顯示', '看', '今天', '明天', '本週', 'show', 'view', 'list']
        # 刪除事件關鍵詞
        delete_keywords = ['刪除', '取消', '移除', 'delete', 'cancel', 'remove']
        # 更新事件關鍵詞
        update_keywords = ['修改', '更改', '調整', 'update', 'modify', 'change']
        
        if any(keyword in user_input_lower for keyword in add_keywords):
            return 'add'
        elif any(keyword in user_input_lower for keyword in view_keywords):
            return 'view'
        elif any(keyword in user_input_lower for keyword in delete_keywords):
            return 'delete'
        elif any(keyword in user_input_lower for keyword in update_keywords):
            return 'update'
        
        return 'help'
    
    def _add_event(self, user_input: str, entities: Dict[str, Any]) -> str:
        """添加事件"""
        try:
            # 提取事件資訊
            event_info = self._extract_event_info(user_input, entities)
            
            if not event_info.get('title'):
                return "❌ 請告訴我要安排什麼事件，例如：「明天下午2點安排與客戶的會議」"
            
            # 創建事件
            event = {
                'id': self.event_id_counter,
                'title': event_info['title'],
                'date': event_info.get('date', '未指定'),
                'time': event_info.get('time', '未指定'),
                'duration': event_info.get('duration', '1小時'),
                'location': event_info.get('location', ''),
                'description': event_info.get('description', ''),
                'created_at': datetime.now().isoformat(),
                'priority': event_info.get('priority', 'normal')
            }
            
            self.events.append(event)
            self.event_id_counter += 1
            
            # 格式化回應
            response = f"""✅ **事件已成功添加！**

📋 **事件詳情**:
🎯 **標題**: {event['title']}
📅 **日期**: {event['date']}
⏰ **時間**: {event['time']}
⌛ **預計時長**: {event['duration']}"""

            if event['location']:
                response += f"\n📍 **地點**: {event['location']}"
            
            if event['description']:
                response += f"\n📝 **備註**: {event['description']}"
            
            response += f"\n\n🔢 **事件ID**: {event['id']}"
            
            # 提供相關建議
            response += self._get_schedule_suggestions(event)
            
            return response
            
        except Exception as e:
            return f"❌ 添加事件時發生錯誤: {str(e)}"
    
    def _extract_event_info(self, user_input: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """提取事件資訊"""
        event_info = {}
        
        # 提取事件標題
        title_patterns = [
            r'安排(.+?)(?:在|的|，|$)',
            r'預約(.+?)(?:在|的|，|$)',
            r'(.+?)會議',
            r'(.+?)活動',
            r'(.+?)課程'
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, user_input)
            if match:
                event_info['title'] = match.group(1).strip()
                break
        
        # 如果沒有找到標題，使用簡化邏輯
        if not event_info.get('title'):
            # 移除時間和日期關鍵詞後的內容作為標題
            clean_input = re.sub(r'(今天|明天|後天|\d+點|\d+:\d+|上午|下午|早上|晚上)', '', user_input)
            clean_input = re.sub(r'(安排|預約|設定)', '', clean_input).strip()
            if clean_input:
                event_info['title'] = clean_input
        
        # 處理日期
        if entities.get('date'):
            date_mapping = {
                'today': datetime.now().strftime('%Y-%m-%d'),
                'tomorrow': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                'day_after_tomorrow': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            }
            event_info['date'] = date_mapping.get(entities['date'], entities['date'])
        else:
            # 從文字中提取日期
            if '今天' in user_input or '今日' in user_input:
                event_info['date'] = datetime.now().strftime('%Y-%m-%d')
            elif '明天' in user_input or '明日' in user_input:
                event_info['date'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            elif '後天' in user_input:
                event_info['date'] = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        
        # 處理時間
        if entities.get('time'):
            event_info['time'] = entities['time']
        else:
            # 從文字中提取時間
            time_patterns = [
                r'(\d{1,2})[點時]',
                r'(\d{1,2}):(\d{2})',
                r'(上午|下午|早上|晚上|中午)(\d{1,2})[點時]?'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, user_input)
                if match:
                    event_info['time'] = match.group(0)
                    break
        
        # 提取地點
        location_patterns = [
            r'在(.+?)(?:舉行|進行|開會|，|$)',
            r'地點[：:](.+?)(?:，|$)',
            r'(?:會議室|辦公室|咖啡廳)(.+?)(?:，|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, user_input)
            if match:
                event_info['location'] = match.group(1).strip()
                break
        
        # 提取時長
        duration_patterns = [
            r'(\d+)小時',
            r'(\d+)分鐘',
            r'(\d+)個小時'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, user_input)
            if match:
                event_info['duration'] = match.group(0)
                break
        
        return event_info
    
    def _view_events(self, entities: Dict[str, Any]) -> str:
        """查看事件"""
        if not self.events:
            return "📅 您目前沒有任何安排的事件。\n\n💡 試試說：「明天下午2點安排與客戶會議」來添加新事件！"
        
        # 確定查看範圍
        view_range = self._determine_view_range(entities)
        filtered_events = self._filter_events_by_range(view_range)
        
        if not filtered_events:
            return f"📅 在{view_range}內沒有安排的事件。"
        
        # 格式化事件列表
        events_text = f"📅 **{view_range}的事件安排**\n\n"
        
        for i, event in enumerate(filtered_events, 1):
            events_text += f"**{i}. {event['title']}**\n"
            events_text += f"   📅 日期: {event['date']}\n"
            events_text += f"   ⏰ 時間: {event['time']}\n"
            events_text += f"   ⌛ 時長: {event['duration']}\n"
            
            if event['location']:
                events_text += f"   📍 地點: {event['location']}\n"
            
            if event['description']:
                events_text += f"   📝 備註: {event['description']}\n"
            
            events_text += f"   🔢 ID: {event['id']}\n\n"
        
        events_text += f"📊 **統計**: 共 {len(filtered_events)} 個事件"
        
        return events_text
    
    def _determine_view_range(self, entities: Dict[str, Any]) -> str:
        """確定查看範圍"""
        if entities.get('date') == 'today' or '今天' in str(entities):
            return '今天'
        elif entities.get('date') == 'tomorrow' or '明天' in str(entities):
            return '明天'
        elif '本週' in str(entities) or '這週' in str(entities):
            return '本週'
        elif '下週' in str(entities):
            return '下週'
        else:
            return '所有'
    
    def _filter_events_by_range(self, range_type: str) -> List[Dict]:
        """根據範圍過濾事件"""
        today = datetime.now().date()
        
        if range_type == '今天':
            target_date = today.strftime('%Y-%m-%d')
            return [e for e in self.events if e['date'] == target_date]
        
        elif range_type == '明天':
            target_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
            return [e for e in self.events if e['date'] == target_date]
        
        elif range_type == '本週':
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            return [e for e in self.events if week_start.strftime('%Y-%m-%d') <= e['date'] <= week_end.strftime('%Y-%m-%d')]
        
        else:
            return self.events
    
    def _delete_event(self, user_input: str) -> str:
        """刪除事件"""
        # 提取事件ID或標題
        event_id = self._extract_event_id(user_input)
        
        if event_id:
            # 根據ID刪除
            for i, event in enumerate(self.events):
                if event['id'] == event_id:
                    deleted_event = self.events.pop(i)
                    return f"✅ 已成功刪除事件「{deleted_event['title']}」"
            
            return f"❌ 找不到ID為 {event_id} 的事件"
        
        else:
            return "❌ 請指定要刪除的事件ID，例如：「刪除事件1」或先查看事件列表獲取ID"
    
    def _extract_event_id(self, text: str) -> int:
        """提取事件ID"""
        # 查找數字
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _update_event(self, user_input: str, entities: Dict[str, Any]) -> str:
        """更新事件"""
        return "🔧 事件更新功能正在開發中，敬請期待！\n\n💡 目前您可以刪除舊事件並添加新事件來達到更新的效果。"
    
    def _get_schedule_suggestions(self, event: Dict) -> str:
        """獲取日程建議"""
        suggestions = "\n\n💡 **貼心提醒**:\n"
        
        # 根據事件類型提供建議
        title_lower = event['title'].lower()
        
        if '會議' in title_lower or 'meeting' in title_lower:
            suggestions += "• 建議提前5-10分鐘到達會議地點\n"
            suggestions += "• 記得準備相關資料和議程\n"
        
        elif '面試' in title_lower or 'interview' in title_lower:
            suggestions += "• 建議提前15分鐘到達\n"
            suggestions += "• 記得準備履歷和相關證件\n"
        
        elif '醫生' in title_lower or '看診' in title_lower:
            suggestions += "• 記得攜帶健保卡和相關病歷\n"
            suggestions += "• 建議提前10分鐘到達\n"
        
        # 時間提醒
        if event['time'] != '未指定':
            suggestions += f"• 我會在事件開始前提醒您\n"
        
        return suggestions
    
    def _provide_schedule_help(self) -> str:
        """提供日程管理幫助"""
        return """📅 **日程管理幫助**

🎯 **我可以幫您**：
• 📝 **添加事件**: 「明天下午2點安排與客戶會議」
• 👀 **查看事件**: 「今天有什麼安排？」
• 🗑️ **刪除事件**: 「刪除事件1」
• 📊 **查看統計**: 「本週有幾個會議？」

💡 **使用技巧**：
• 盡量提供完整資訊（時間、地點、事件內容）
• 可以使用相對時間（今天、明天、下週）
• 每個事件都有唯一ID，刪除時請使用ID

🚀 **即將推出**：
• 事件提醒功能
• 重複事件設定
• 日程衝突檢測
• 與Google Calendar同步

試試看說：「明天上午10點安排產品會議，地點在會議室A」"""