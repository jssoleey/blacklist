# llm.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 불러오기 (.env 파일 사용 시)
env_path = os.path.join(os.path.dirname(__file__), '.envfile')
load_dotenv(dotenv_path=env_path)
api_key = os.getenv("OPENAI_API_KEY")  # 또는 직접 입력 가능

client = OpenAI(api_key=api_key)

def generate_advice(customer_name: str, tags: list, consult_content: str, author: str) -> str:
    tag_text = ", ".join(tags) if tags else "없음"

    prompt = f"""
    너는 보험 민원 응대를 지원하는 AI 어시스턴트야.
    상담원이 작성한 블랙리스트 민원 상황을 기반으로, 아래의 형식과 지침에 맞춰 실질적인 대응 조언을 제공해줘.

    [상담 상황 요약]
    - 고객명: {customer_name}
    - 관련 태그: {tag_text}
    - 상담 내용:
    {consult_content}

    [출력 형식 및 지침]

    1. 전체 출력은 Markdown 형식으로 구성할 것
    2. 각 항목은 제목 앞에 이모지를 붙여 강조하고, 제목은 <h5> 크기의 두꺼운 글씨로 작성할 것.
    3. CHAT GPT가 답변하듯이, 마크다운 형식을 적극적으로 이용하여여 사용자의 가독성을 높일 것것
    4. 항목별 설명은 실무적으로 유용하고 구체적인 문장으로 작성할 것

    [조언 항목 예시]
    1. **고객 유형 분석**  
    - 고객의 태도나 언어적 특성을 바탕으로 어떤 민원 유형인지 설명

    2. **유의사항**  
    - 상담 중 실수하기 쉬운 포인트, 감정 유발 가능성 등 주의점

    3. **추천 대응 전략**  
    - 실전에서 상담원이 바로 사용할 수 있는 대응 문장 예시 포함

    4. **팀팀 공유 메모**  
    - 동료 상담원들과 공유하면 좋을 요점 정리 (짧게 핵심 위주로)

    너는 전문가답게 신중하고 공감 있는 톤으로 작성해줘. 너무 형식적이거나 일반적인 문장보다는 현장에서 바로 사용할 수 있는 조언을 부탁해.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "너는 보험 민원 대응 전문가 AI야. 신중하고 구체적으로 조언해줘."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"[⚠️ 오류 발생] AI 응답을 생성할 수 없습니다.\n{str(e)}"

def generate_title(customer_name: str, tags: list, consult_content: str) -> str:
    tag_text = ", ".join(tags) if tags else "없음"
    prompt = f"""
너는 보험 민원 데이터를 요약해주는 AI야.
아래의 고객 민원 상황을 바탕으로, 목록에 표시할 짧고 간결한 제목을 하나 만들어줘.
너무 길지 않게 핵심 위주로 작성하고, 격식 없이 실무자들이 한눈에 파악할 수 있도록 표현해줘.

[고객명]: {customer_name}
[관련 태그]: {tag_text}
[상담 내용]:
{consult_content}

[제목 출력 형식]
상황에 맞는 한 줄 제목
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "너는 고객 민원 데이터를 요약해서 제목을 만들어주는 AI야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "제목 없음"
