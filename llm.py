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
상담원이 작성한 블랙리스트 민원 상황을 기반으로 아래의 형식에 따라 조언을 제공해줘.

[상담 상황 요약]
- 고객명: {customer_name}
- 관련 태그: {tag_text}
- 상담 내용:
{consult_content}

[조언 형식]
1. 고객 유형 분석
2. 유의사항
3. 추천 대응 전략
4. 팀 공유 메모

조언은 신중하고 실무적으로 유용하게 작성해줘.
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
