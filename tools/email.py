from datetime import datetime
from typing import Dict, List, Any
import re
import json

class EmailTool:
    """郵件處理工具"""
    
    def __init__(self):
        """初始化郵件工具"""
        # 在實際應用中，這裡會連接到真實的郵件服務
        # 現在我們使用模擬數據作為演示
        self.mock_emails = [
            {
                'id': 1,
                'from': 'john.doe@company.com',
                'to': 'user@email.com',
                'subject': '週會議程確認',
                'body': '請確認明天的週會議程，會議時間是上午10點。',
                'date': '2024-06-11',
                'read': False,
                'priority': 'normal'
            },
            {
                'id': 2,
                'from': 'hr@company.com',
                'to': 'user@email.com', 
                'subject': '年假申請審核',
                'body': '您的年假申請已通過審核，請查看附件。',
                'date': '2024-06-10',
                'read': True,
                'priority': 'high'
            },
            {
                'id': 3,
                'from': 'client@external.com',
                'to': 'user@email.com',
                'subject': '專案進度詢問',
                'body': '想了解一下目前專案的進度如何？預計什麼時候可以完成？',
                'date': '2024-06-09',
                'read': False,
                'priority': 'urgent'
            }
        ]
        
        self.draft_emails = []
        self.templates = {
            'meeting_invite': {
                'subject': '會議邀請 - {topic}',
                'body': """親愛的 {recipient}，

希望您一切安好。

我想邀請您參加關於「{topic}」的會議。

會議詳情：
• 時間：{datetime}
• 地點：{location}
• 預計時長：{duration}

議程：
{agenda}

請回覆確認您是否能夠參加。

謝謝！

最佳問候，
{sender}"""
            },
            'project_update': {
                'subject': '專案進度更新 - {project_name}',
                'body': """您好，

這是關於「{project_name}」專案的進度更新。

目前狀況：
• 完成度：{progress}%
• 預計完成時間：{estimated_completion}
• 主要里程碑：{milestones}

如有任何問題，請隨時聯繫我。

謝謝！

{sender}"""
            },
            'follow_up': {
                'subject': '後續追蹤 - {topic}',
                'body': """您好，

希望您一切順利。

我想跟進我們之前討論的「{topic}」。

{follow_up_content}

期待您的回覆。

謝謝！

{sender}"""
            }
        }
    
    def process_email(self, user_input: str) -> str:
        """
        處理郵件相關請求
        
        Args:
            user_input: 用戶輸入
            
        Returns:
            處理結果
        """
        # 檢測郵件操作意圖
        intent = self._detect_email_intent(user_input)
        
        if intent == 'read':
            return self._read_emails(user_input)
        elif intent == 'compose':
            return self._compose_email(user_input)
        elif intent == 'reply':
            return self._reply_email(user_input)
        elif intent == 'search':
            return self._search_emails(user_input)
        elif intent == 'summary':
            return self._summarize_emails()
        elif intent == 'template':
            return self._use_template(user_input)
        else:
            return self._provide_email_help()
    
    def _detect_email_intent(self, user_input: str) -> str:
        """檢測郵件操作意圖"""
        user_input_lower = user_input.lower()
        
        # 閱讀郵件
        read_keywords = ['查看', '讀', '顯示', '郵件', '信件', 'read', 'show', 'view']
        # 撰寫郵件  
        compose_keywords = ['寫', '撰寫', '發送', '寄', 'compose', 'write', 'send']
        # 回覆郵件
        reply_keywords = ['回覆', '回信', 'reply', 'respond']
        # 搜尋郵件
        search_keywords = ['搜尋', '查找', '找', 'search', 'find']
        # 摘要
        summary_keywords = ['摘要', '總結', '概要', 'summary', 'overview']
        # 模板
        template_keywords = ['模板', '範本', 'template']
        
        if any(keyword in user_input_lower for keyword in read_keywords):
            return 'read'
        elif any(keyword in user_input_lower for keyword in compose_keywords):
            return 'compose'
        elif any(keyword in user_input_lower for keyword in reply_keywords):
            return 'reply'
        elif any(keyword in user_input_lower for keyword in search_keywords):
            return 'search'
        elif any(keyword in user_input_lower for keyword in summary_keywords):
            return 'summary'
        elif any(keyword in user_input_lower for keyword in template_keywords):
            return 'template'
        
        return 'help'
    
    def _read_emails(self, user_input: str) -> str:
        """讀取郵件"""
        # 檢查是否指定特定郵件
        email_id = self._extract_email_id(user_input)
        
        if email_id:
            # 讀取特定郵件
            email = self._find_email_by_id(email_id)
            if email:
                email['read'] = True  # 標記為已讀
                return self._format_single_email(email)
            else:
                return f"❌ 找不到ID為 {email_id} 的郵件"
        
        # 根據條件過濾郵件
        if '未讀' in user_input or 'unread' in user_input.lower():
            emails = [e for e in self.mock_emails if not e['read']]
            title = "📧 **未讀郵件**"
        elif '重要' in user_input or 'important' in user_input.lower():
            emails = [e for e in self.mock_emails if e['priority'] in ['high', 'urgent']]
            title = "⚡ **重要郵件**"
        else:
            emails = self.mock_emails[-5:]  # 最新5封
            title = "📧 **最新郵件**"
        
        if not emails:
            return "📪 沒有找到符合條件的郵件。"
        
        return self._format_email_list(emails, title)
    
    def _format_email_list(self, emails: List[Dict], title: str) -> str:
        """格式化郵件列表"""
        result = f"{title}\n\n"
        
        for i, email in enumerate(emails, 1):
            # 優先級圖標
            priority_icon = {
                'urgent': '🔴',
                'high': '🟡', 
                'normal': '🟢'
            }.get(email['priority'], '🟢')
            
            # 已讀狀態
            read_status = '✅' if email['read'] else '🆕'
            
            result += f"**{i}. {email['subject']}** {priority_icon} {read_status}\n"
            result += f"   📤 寄件者: {email['from']}\n"
            result += f"   📅 日期: {email['date']}\n"
            result += f"   📝 預覽: {email['body'][:50]}...\n"
            result += f"   🔢 ID: {email['id']}\n\n"
        
        result += f"📊 **統計**: 共 {len(emails)} 封郵件\n"
        result += "💡 使用「查看郵件{ID}」來讀取完整內容"
        
        return result
    
    def _format_single_email(self, email: Dict) -> str:
        """格式化單封郵件"""
        priority_icon = {
            'urgent': '🔴 緊急',
            'high': '🟡 重要',
            'normal': '🟢 一般'
        }.get(email['priority'], '🟢 一般')
        
        return f"""📧 **郵件詳情**

📋 **主旨**: {email['subject']}
📤 **寄件者**: {email['from']}
📥 **收件者**: {email['to']}
📅 **日期**: {email['date']}
⚡ **優先級**: {priority_icon}

📝 **內容**:
{email['body']}

---
💡 **操作建議**: 
• 回覆此郵件：「回覆郵件{email['id']}」
• 標記為重要：「標記郵件{email['id']}為重要」"""
    
    def _compose_email(self, user_input: str) -> str:
        """撰寫郵件"""
        # 提取郵件資訊
        email_info = self._extract_email_info(user_input)
        
        if not email_info.get('subject') and not email_info.get('recipient'):
            return """✉️ **撰寫新郵件**

請提供更多資訊來幫您撰寫郵件：

📝 **範例用法**：
• 「寫一封關於會議安排的郵件給john@company.com」
• 「撰寫專案進度更新郵件」
• 「寄信給客戶詢問需求」

🎯 **需要的資訊**：
• 收件者（誰）
• 主旨（什麼事）
• 內容要點

💡 **或者使用模板**：「使用會議邀請模板」"""
        
        # 生成郵件草稿
        draft = self._generate_email_draft(email_info)
        
        return f"""✉️ **郵件草稿已生成**

{draft}

---
💡 **下一步**：
• 修改內容：「修改主旨為...」
• 發送郵件：「發送這封郵件」（演示模式）
• 使用模板：「使用會議邀請模板」"""
    
    def _extract_email_info(self, user_input: str) -> Dict[str, str]:
        """提取郵件資訊"""
        info = {}
        
        # 提取收件者
        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        emails = re.findall(email_pattern, user_input)
        if emails:
            info['recipient'] = emails[0]
        
        # 提取主旨關鍵詞
        subject_patterns = [
            r'關於(.+?)的',
            r'(.+?)郵件',
            r'主旨[：:](.+?)(?:，|$)',
            r'標題[：:](.+?)(?:，|$)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, user_input)
            if match:
                info['subject'] = match.group(1).strip()
                break
        
        # 推斷郵件類型
        if '會議' in user_input:
            info['type'] = 'meeting'
            if not info.get('subject'):
                info['subject'] = '會議安排'
        elif '專案' in user_input or '項目' in user_input:
            info['type'] = 'project'
            if not info.get('subject'):
                info['subject'] = '專案相關'
        elif '詢問' in user_input or '請問' in user_input:
            info['type'] = 'inquiry'
            if not info.get('subject'):
                info['subject'] = '詢問'
        
        return info
    
    def _generate_email_draft(self, email_info: Dict[str, str]) -> str:
        """生成郵件草稿"""
        recipient = email_info.get('recipient', '[收件者]')
        subject = email_info.get('subject', '[主旨]')
        email_type = email_info.get('type', 'general')
        
        # 根據類型生成內容
        if email_type == 'meeting':
            body = """您好，

希望您一切安好。

我想與您安排一個會議來討論相關事宜。

會議詳情：
• 時間：[請填入時間]
• 地點：[請填入地點]
• 議程：[請填入議程]

請回覆確認您是否能夠參加。

謝謝！

最佳問候"""
        
        elif email_type == 'project':
            body = """您好，

關於我們目前進行的專案，我想與您分享一些更新。

[請填入專案詳情]

如有任何問題或建議，請隨時聯繫我。

謝謝！"""
        
        elif email_type == 'inquiry':
            body = """您好，

我想詢問關於 [請填入詢問內容] 的相關資訊。

[請填入具體問題]

期待您的回覆。

謝謝！"""
        
        else:
            body = """您好，

[請填入郵件內容]

謝謝！"""
        
        return f"""**收件者**: {recipient}
**主旨**: {subject}

**內容**:
{body}"""
    
    def _reply_email(self, user_input: str) -> str:
        """回覆郵件"""
        email_id = self._extract_email_id(user_input)
        
        if not email_id:
            return "❌ 請指定要回覆的郵件ID，例如：「回覆郵件1」"
        
        original_email = self._find_email_by_id(email_id)
        if not original_email:
            return f"❌ 找不到ID為 {email_id} 的郵件"
        
        # 生成回覆草稿
        reply_draft = f"""✉️ **回覆郵件草稿**

**收件者**: {original_email['from']}
**主旨**: Re: {original_email['subject']}

**內容**:
您好，

謝謝您的郵件。

[請填入回覆內容]

如有任何問題，請隨時聯繫我。

謝謝！

---
**原始郵件**:
寄件者: {original_email['from']}
主旨: {original_email['subject']}
內容: {original_email['body'][:100]}...

---
💡 **下一步**: 「修改回覆內容」或「發送回覆」"""
        
        return reply_draft
    
    def _search_emails(self, user_input: str) -> str:
        """搜尋郵件"""
        # 提取搜尋關鍵詞
        search_keywords = self._extract_search_keywords(user_input)
        
        if not search_keywords:
            return "🔍 請提供搜尋關鍵詞，例如：「搜尋包含會議的郵件」"
        
        # 搜尋郵件
        results = []
        for email in self.mock_emails:
            for keyword in search_keywords:
                if (keyword.lower() in email['subject'].lower() or 
                    keyword.lower() in email['body'].lower() or
                    keyword.lower() in email['from'].lower()):
                    results.append(email)
                    break
        
        if not results:
            return f"🔍 沒有找到包含「{', '.join(search_keywords)}」的郵件"
        
        return self._format_email_list(results, f"🔍 **搜尋結果** (關鍵詞: {', '.join(search_keywords)})")
    
    def _extract_search_keywords(self, user_input: str) -> List[str]:
        """提取搜尋關鍵詞"""
        # 移除搜尋指令詞
        clean_input = re.sub(r'(搜尋|查找|找|包含|關於|search|find)', '', user_input, flags=re.IGNORECASE)
        clean_input = clean_input.strip()
        
        # 分割關鍵詞
        keywords = [kw.strip() for kw in clean_input.split() if len(kw.strip()) > 1]
        return keywords
    
    def _summarize_emails(self) -> str:
        """郵件摘要"""
        total_emails = len(self.mock_emails)
        unread_emails = len([e for e in self.mock_emails if not e['read']])
        urgent_emails = len([e for e in self.mock_emails if e['priority'] == 'urgent'])
        
        # 最新未讀郵件
        latest_unread = [e for e in self.mock_emails if not e['read']][-3:]
        
        summary = f"""📊 **郵件摘要**

📈 **統計資訊**:
• 總郵件數: {total_emails}
• 未讀郵件: {unread_emails}
• 緊急郵件: {urgent_emails}

🆕 **最新未讀郵件**:"""
        
        for email in latest_unread:
            summary += f"\n• {email['subject']} (來自: {email['from']})"
        
        summary += f"""

💡 **建議行動**:
• 查看未讀郵件: 「查看未讀郵件」
• 處理緊急郵件: 「查看重要郵件」
• 回覆待處理: 「回覆郵件{latest_unread[0]['id'] if latest_unread else 1}」"""
        
        return summary
    
    def _use_template(self, user_input: str) -> str:
        """使用郵件模板"""
        template_name = self._detect_template_type(user_input)
        
        if template_name not in self.templates:
            available_templates = list(self.templates.keys())
            return f"""📋 **可用的郵件模板**:

🎯 **模板類型**:
• **meeting_invite** - 會議邀請
• **project_update** - 專案進度更新  
• **follow_up** - 後續追蹤

💡 **使用方法**: 「使用會議邀請模板」

📝 **自定義**: 告訴我您需要什麼類型的郵件，我可以為您創建模板！"""
        
        template = self.templates[template_name]
        
        return f"""📋 **{template_name} 模板**

**主旨模板**: {template['subject']}

**內容模板**:
{template['body']}

---
💡 **使用說明**:
• 將 {{參數}} 替換為實際內容
• 例如 {{topic}} 替換為實際主題
• 「使用此模板寫郵件給john@company.com」"""
    
    def _detect_template_type(self, user_input: str) -> str:
        """檢測模板類型"""
        user_input_lower = user_input.lower()
        
        if '會議' in user_input_lower or 'meeting' in user_input_lower:
            return 'meeting_invite'
        elif '專案' in user_input_lower or 'project' in user_input_lower:
            return 'project_update'
        elif '追蹤' in user_input_lower or 'follow' in user_input_lower:
            return 'follow_up'
        
        return 'meeting_invite'  # 預設
    
    def _extract_email_id(self, text: str) -> int:
        """提取郵件ID"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None
    
    def _find_email_by_id(self, email_id: int) -> Dict:
        """根據ID查找郵件"""
        for email in self.mock_emails:
            if email['id'] == email_id:
                return email
        return None
    
    def _provide_email_help(self) -> str:
        """提供郵件幫助"""
        return """📧 **郵件管理幫助**

🎯 **我可以幫您**：
• 📖 **讀取郵件**: 「查看最新郵件」、「讀取未讀郵件」
• ✍️ **撰寫郵件**: 「寫郵件給john@company.com關於會議」
• 💬 **回覆郵件**: 「回覆郵件1」
• 🔍 **搜尋郵件**: 「搜尋包含專案的郵件」
• 📊 **郵件摘要**: 「郵件摘要」
• 📋 **使用模板**: 「使用會議邀請模板」

💡 **實用功能**：
• 查看特定郵件：「查看郵件{ID}」
• 按優先級篩選：「查看重要郵件」
• 郵件統計：「有多少未讀郵件？」

🚀 **即將推出**：
• 郵件自動分類
• 智能回覆建議
• 郵件排程發送
• 與Gmail/Outlook同步

試試說：「查看未讀郵件」或「寫郵件給客戶」"""