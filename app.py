

#st.title("실시간 환율 챗봇")
# st.title("_Streamlit_ is :blue[cool] :sunglasses:")
# st.title("Dashboard", icon=":material/dashboard:")

# st.badge('New')

# st.markdown("*Streamlit* is **really** ***cool***.")

import streamlit as st
from dotenv import load_dotenv # 환경파일 불러오기위한 함수 환경파일엔 개인정보들 유출되면 안되는 것들이 담겨있음
#모델 객체 생성
from langchain.chat_models import init_chat_model
# 도구 생성
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
import requests

st.title("실시간 환율 챗봇")

load_dotenv()
model = init_chat_model('gpt-5.4-mini')


Tavily_Search = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)


@tool
def get_weather(location : str) -> str:
    '''특정 지역의 날씨 정보 조회 도구'''
    return f'{location}의 날씨는 -5도에 미세먼지는 매우 나쁨'

@tool
def get_exchange_rate(base: str = "USD", quote: str = "KRW", amount: float = 1.0) -> str:
    """
    특정 통화의 환율을 조회합니다.
    예: base='USD', quote='KRW'이면 1달러가 몇 원인지 조회합니다.
    amount를 넣으면 해당 금액을 환산합니다.
    """

    base = base.upper()
    quote = quote.upper()

    url = f"https://api.frankfurter.dev/v2/rate/{base}/{quote}"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()

    rate = data["rate"]
    date = data.get("date", "알 수 없음")

    converted = amount * rate

    return (
        f"기준일: {date}\n"
        f"환율: 1 {base} = {rate:,.2f} {quote}\n"
        f"환산: {amount:,.2f} {base} = {converted:,.2f} {quote}"
    )





agent = create_agent(model, tools=[get_weather, get_exchange_rate ,Tavily_Search],
                         system_prompt="""
                            너는 환율 정보를 알려주는 친절한 금융 정보 assistant다.

                            사용자가 원-달러 환율, 달러 환율, USD/KRW 환율을 물어보면
                            반드시 get_exchange_rate Tool을 사용해 최신 환율을 조회해라.

                            한국에서 말하는 '원-달러 환율'은 보통
                            '1달러가 몇 원인지', 즉 USD -> KRW 환율을 의미한다.

                            답변에는 반드시 다음을 포함해라.
                            1. 기준일
                            2. Frankfurter API 기준이라는 설명

                            투자 조언처럼 말하지 말고, 조회된 환율 정보만 간단히 설명해라.
                            """,
                     )






## 챗봇 구현
if 'messages' not in st.session_state:
    st.session_state.messages = []

prompt = st.chat_input('무엇이든 물어보세요')


if prompt:
    response = agent.invoke(
        {'messages' : [{'role' : 'user', 'content' : prompt}]}
    )
    st.session_state.messages.append({'role' : 'user', 'content': prompt})
    st.session_state.messages.append({'role' : 'ai', 'content': response['messages'][-1].content})

for message in st.session_state.messages :
    with st.chat_message(message['role']):
        st.write(message['content'])





