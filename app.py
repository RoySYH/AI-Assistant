import streamlit as st
import os
from datetime import datetime
import json
from agent_core import PersonalAssistant
from memory import ConversationMemory

# 頁面配置
st.set_page_config(
    page_title="🤖 智能個人助理",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.chat-message {
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.user-message {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    margin-left: 20%;
}
.assistant-message {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    margin-right: 20%;
}
.feature-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    margin: 1rem 0;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'memory' not in st.session_state:
        st.session_state.memory = ConversationMemory()

def setup_sidebar():
    """設置側邊欄"""
    with st.sidebar:
        st.markdown("## ⚙️ 配置設定")
        
        # API 配置
        st.markdown("### 🔐 API 設定")
        gemini_key = st.text_input("Gemini API Key", type="password", key="gemini_key")
        weather_key = st.text_input("Weather API Key", type="password", key="weather_key")
        
        if st.button("🔄 初始化助理", type="primary"):
            if gemini_key:
                try:
                    os.environ["GEMINI_API_KEY"] = gemini_key
                    os.environ["WEATHER_API_KEY"] = weather_key
                    st.session_state.assistant = PersonalAssistant(gemini_key, weather_key)
                    st.success("✅ 助理初始化成功！")
                except Exception as e:
                    st.error(f"❌ 初始化失敗: {str(e)}")
            else:
                st.error("❌ 請輸入 Gemini API Key")
        
        st.markdown("---")
        
        # 功能說明
        st.markdown("### 🎯 主要功能")
        features = [
            "🌤️ 即時天氣查詢",
            "📅 智能日程管理", 
            "📧 郵件處理助手",
            "🧠 上下文記憶",
            "💬 自然語言對話"
        ]
        for feature in features:
            st.markdown(f"- {feature}")
        
        st.markdown("---")
        
        # 記憶管理
        st.markdown("### 🧠 記憶管理")
        if st.button("🗑️ 清除對話記錄", type="secondary"):
            st.session_state.messages = []
            st.session_state.memory.clear_memory()
            st.success("✅ 記錄已清除")
        
        # 顯示記憶統計
        if st.session_state.memory:
            memory_count = len(st.session_state.memory.get_recent_memories())
            st.metric("記憶條數", memory_count)

def display_chat_interface():
    """顯示聊天界面"""
    st.markdown('<h1 class="main-header">🤖 智能個人助理</h1>', unsafe_allow_html=True)
    
    # 顯示歡迎訊息
    if not st.session_state.messages:
        welcome_col1, welcome_col2, welcome_col3 = st.columns(3)
        
        with welcome_col1:
            st.markdown("""
            <div class="feature-card">
                <h3>🌤️ 天氣服務</h3>
                <p>查詢全球任何城市的即時天氣資訊</p>
                <small>試試說："今天台北天氣如何？"</small>
            </div>
            """, unsafe_allow_html=True)
        
        with welcome_col2:
            st.markdown("""
            <div class="feature-card">
                <h3>📅 日程管理</h3>
                <p>智能管理你的日程安排</p>
                <small>試試說："幫我安排明天的會議"</small>
            </div>
            """, unsafe_allow_html=True)
        
        with welcome_col3:
            st.markdown("""
            <div class="feature-card">
                <h3>🧠 智能記憶</h3>
                <p>記住我們的對話內容</p>
                <small>我會記住你說過的重要資訊</small>
            </div>
            """, unsafe_allow_html=True)
    
    # 顯示對話歷史
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>👤 您:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 助理:</strong><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
    
    # 輸入區域
    user_input = st.chat_input("輸入您的問題或需求...")
    
    if user_input and st.session_state.assistant:
        # 添加用戶訊息
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 處理用戶請求
        with st.spinner("🤔 思考中..."):
            try:
                # 獲取相關記憶
                relevant_memories = st.session_state.memory.get_relevant_memories(user_input)
                
                # 生成回應
                response = st.session_state.assistant.process_request(
                    user_input, 
                    relevant_memories,
                    st.session_state.messages[-5:]  # 最近5條對話
                )
                
                # 添加助理回應
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # 儲存到記憶
                st.session_state.memory.add_memory(user_input, response)
                
                # 重新運行以顯示新訊息
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 處理請求時發生錯誤: {str(e)}")
    
    elif user_input and not st.session_state.assistant:
        st.warning("⚠️ 請先在側邊欄配置並初始化助理！")

def main():
    """主函數"""
    initialize_session_state()
    setup_sidebar()
    display_chat_interface()
    
    # 頁腳
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🚀 <strong>智能個人助理系統</strong> | 使用 Streamlit + LangChain + Google Gemini 構建</p>
        <p>💡 這是一個展示 Agentic AI 能力的 Side Project</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()