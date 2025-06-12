from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import re
from collections import defaultdict

class ConversationMemory:
    """對話記憶管理系統"""
    
    def __init__(self, max_memories: int = 100):
        """
        初始化記憶系統
        
        Args:
            max_memories: 最大記憶條數
        """
        self.max_memories = max_memories
        self.memories = []
        self.user_preferences = {}
        self.important_facts = {}
        
    def add_memory(self, user_input: str, assistant_response: str, importance: float = 0.5):
        """
        添加記憶
        
        Args:
            user_input: 用戶輸入
            assistant_response: 助理回應
            importance: 重要性分數 (0.0-1.0)
        """
        memory = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'assistant_response': assistant_response,
            'importance': importance,
            'keywords': self._extract_keywords(user_input + " " + assistant_response),
            'category': self._categorize_memory(user_input)
        }
        
        self.memories.append(memory)
        
        # 提取用戶偏好
        self._extract_user_preferences(user_input)
        
        # 提取重要事實
        self._extract_important_facts(user_input, assistant_response)
        
        # 清理舊記憶
        self._cleanup_memories()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 移除標點符號並轉為小寫
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # 停用詞列表
        stop_words = {
            '的', '是', '在', '了', '有', '和', '就', '都', '而', '及', '與', '或',
            '但', '不', '沒', '很', '還', '也', '只', '再', '更', '最', '非常',
            'the', 'is', 'at', 'which', 'on', 'and', 'a', 'to', 'as', 'are',
            'was', 'will', 'be', 'have', 'has', 'had', 'do', 'does', 'did'
        }
        
        # 分詞並過濾
        words = text.split()
        keywords = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 返回前10個關鍵詞
        return keywords[:10]
    
    def _categorize_memory(self, user_input: str) -> str:
        """記憶分類"""
        categories = {
            'weather': ['天氣', '氣溫', '下雨', '晴天', 'weather'],
            'schedule': ['會議', '安排', '日程', '約會', 'meeting', 'schedule'],
            'email': ['郵件', '信件', '寄信', 'email', 'mail'],
            'personal': ['我', '我的', '個人', '喜歡', '偏好', 'my', 'personal'],
            'work': ['工作', '公司', '同事', '專案', 'work', 'project', 'company'],
            'general': []
        }
        
        user_input_lower = user_input.lower()
        
        for category, keywords in categories.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _extract_user_preferences(self, user_input: str):
        """提取用戶偏好"""
        # 偏好關鍵詞模式
        preference_patterns = [
            (r'我喜歡(.+)', 'likes'),
            (r'我不喜歡(.+)', 'dislikes'),
            (r'我的(.+)是(.+)', 'attributes'),
            (r'我住在(.+)', 'location'),
            (r'我的工作是(.+)', 'job'),
            (r'我叫(.+)', 'name')
        ]
        
        for pattern, pref_type in preference_patterns:
            matches = re.findall(pattern, user_input)
            if matches:
                if pref_type not in self.user_preferences:
                    self.user_preferences[pref_type] = []
                self.user_preferences[pref_type].extend(matches)
    
    def _extract_important_facts(self, user_input: str, assistant_response: str):
        """提取重要事實"""
        # 重要事實模式
        fact_patterns = [
            r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 日期
            r'(\d{1,2}:\d{2})',  # 時間
            r'([\d\w\s]+(?:會議|活動|約會))',  # 事件
            r'([\w\s]+@[\w\s]+\.[\w\s]+)',  # 郵件地址
            r'(\d{4}-\d{4}-\d{4})',  # 電話號碼
        ]
        
        text = user_input + " " + assistant_response
        
        for pattern in fact_patterns:
            matches = re.findall(pattern, text)
            if matches:
                timestamp = datetime.now().isoformat()
                for match in matches:
                    fact_key = f"{timestamp}_{match}"
                    self.important_facts[fact_key] = {
                        'content': match,
                        'timestamp': timestamp,
                        'context': user_input[:100]  # 保存上下文
                    }
    
    def _cleanup_memories(self):
        """清理舊記憶"""
        if len(self.memories) > self.max_memories:
            # 按重要性和時間排序，保留重要的記憶
            self.memories.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
            self.memories = self.memories[:self.max_memories]
    
    def get_relevant_memories(self, query: str, limit: int = 5) -> List[str]:
        """
        獲取相關記憶
        
        Args:
            query: 查詢字符串
            limit: 返回記憶數量限制
            
        Returns:
            相關記憶列表
        """
        if not self.memories:
            return []
        
        query_keywords = set(self._extract_keywords(query))
        relevant_memories = []
        
        for memory in self.memories:
            # 計算相關性分數
            memory_keywords = set(memory['keywords'])
            keyword_overlap = len(query_keywords.intersection(memory_keywords))
            
            if keyword_overlap > 0:
                relevance_score = (
                    keyword_overlap / len(query_keywords.union(memory_keywords)) * 0.7 +
                    memory['importance'] * 0.3
                )
                
                relevant_memories.append({
                    'memory': memory,
                    'score': relevance_score
                })
        
        # 按相關性排序
        relevant_memories.sort(key=lambda x: x['score'], reverse=True)
        
        # 格式化返回結果
        result = []
        for item in relevant_memories[:limit]:
            memory = item['memory']
            timestamp = datetime.fromisoformat(memory['timestamp']).strftime('%m-%d %H:%M')
            result.append(f"[{timestamp}] 用戶: {memory['user_input'][:50]}...")
        
        return result
    
    def get_recent_memories(self, hours: int = 24) -> List[Dict]:
        """
        獲取最近的記憶
        
        Args:
            hours: 時間範圍（小時）
            
        Returns:
            最近記憶列表
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []
        
        for memory in self.memories:
            memory_time = datetime.fromisoformat(memory['timestamp'])
            if memory_time >= cutoff_time:
                recent_memories.append(memory)
        
        return sorted(recent_memories, key=lambda x: x['timestamp'], reverse=True)
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """獲取用戶偏好"""
        return self.user_preferences.copy()
    
    def get_important_facts(self) -> Dict[str, Any]:
        """獲取重要事實"""
        return self.important_facts.copy()
    
    def search_memories(self, keyword: str) -> List[Dict]:
        """
        搜索記憶
        
        Args:
            keyword: 搜索關鍵詞
            
        Returns:
            匹配的記憶列表
        """
        results = []
        keyword_lower = keyword.lower()
        
        for memory in self.memories:
            if (keyword_lower in memory['user_input'].lower() or 
                keyword_lower in memory['assistant_response'].lower() or
                keyword_lower in ' '.join(memory['keywords'])):
                results.append(memory)
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """獲取記憶統計資訊"""
        if not self.memories:
            return {
                'total_memories': 0,
                'categories': {},
                'average_importance': 0.0
            }
        
        categories = defaultdict(int)
        total_importance = 0
        
        for memory in self.memories:
            categories[memory['category']] += 1
            total_importance += memory['importance']
        
        return {
            'total_memories': len(self.memories),
            'categories': dict(categories),
            'average_importance': total_importance / len(self.memories),
            'user_preferences_count': len(self.user_preferences),
            'important_facts_count': len(self.important_facts)
        }
    
    def clear_memory(self):
        """清除所有記憶"""
        self.memories.clear()
        self.user_preferences.clear()
        self.important_facts.clear()
    
    def export_memories(self) -> str:
        """導出記憶為JSON格式"""
        export_data = {
            'memories': self.memories,
            'user_preferences': self.user_preferences,
            'important_facts': self.important_facts,
            'export_timestamp': datetime.now().isoformat()
        }
        return json.dumps(export_data, ensure_ascii=False, indent=2)
    
    def import_memories(self, json_data: str):
        """從JSON數據導入記憶"""
        try:
            data = json.loads(json_data)
            self.memories = data.get('memories', [])
            self.user_preferences = data.get('user_preferences', {})
            self.important_facts = data.get('important_facts', {})
            return True
        except Exception as e:
            print(f"導入記憶失敗: {e}")
            return False