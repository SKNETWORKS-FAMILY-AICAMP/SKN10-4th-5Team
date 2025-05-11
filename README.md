
# SK네트웍스 Family AI Camp 훈련 도우미
<img width="929" alt="Screenshot 2025-05-12 at 5 49 15 AM" src="https://github.com/user-attachments/assets/2718f7ba-9420-41e2-abb7-8e0817e04d67" />

## 프로젝트 개요

이 챗봇은 SK네트웍스 Family AI Camp의 수강생, 매니저, 강사 등 캠프 구성원들이  
실시간으로 정보를 얻고, 고민을 상담하며, 캠프 생활을 더 편리하게 할 수 있도록  
설계된 **AI 매니저 '하루(HARU)'** 챗봇 시스템입니다.

---

## 주요 기능

- **실시간 대화**  
  - 캠프 일정, 출결, 시설, 학습, 생활 등 다양한 질문에 즉각 응답
  - 친근하고 전문적인 하루 캐릭터의 말투와 응원 메시지

- **RAG 기반 지능형 검색**  
  - campusfaq.csv, PDF, 텍스트 등 다양한 문서에서 의미적으로 관련 있는 정보를 찾아 답변
  - OpenAI 임베딩을 활용한 벡터 검색 + LLM 생성 결합

- **추천 질문/예시 질문 제공**  
  - 자주 묻는 질문을 랜덤으로 추천하여 사용자의 탐색 편의성 향상

- **상황별 안내 및 에러 처리**  
  - 확실하지 않은 정보는 담당 매니저 안내
  - 오류 발생 시 친절한 사과 메시지와 대체 질문 제안

- **프론트엔드 인터랙션**  
  - 추천 질문 버튼, 감정 상태 등

---
<img width="1174" alt="Screenshot 2025-05-12 at 5 45 07 AM" src="https://github.com/user-attachments/assets/34d44547-6792-44d4-8082-fc5cd07a581c" />

## 시스템 구조




### 1. **백엔드**

#### `chatbot_logic.py`
- **문서 데이터 로딩**: FAQ, CSV, TXT, PDF 등 다양한 소스에서 문서 수집
- **임베딩(벡터화)**: OpenAI 임베딩 API로 모든 문서와 질문을 벡터화
- **유사도 검색**: 코사인 유사도로 질문과 가장 비슷한 문서 K개 추출
- **LLM 답변 생성**: 관련 문서(컨텍스트)와 함께 OpenAI GPT-3.5-turbo로 답변 생성
- **추천 질문**: FAQ 기반 랜덤 추천 질문 제공
- **에러 처리**: 예외 발생 시 사과 메시지와 추천 질문 반환

#### `document_processor.py`
- **텍스트 청크 분할**: 긴 문서를 LLM 입력에 맞게 청크로 분할
- **(확장 예정) 쿼리 강화**: 대화 히스토리 기반 쿼리 가공

---

### 2. **프론트엔드**

#### `chat.html`
- **챗봇 UI**: 대화창, 입력창, 추천 질문, 감정 상태, 캐릭터 영역 등
- **캐릭터 시각화**: SVG
- **추천 질문 버튼**: 클릭 시 입력창에 자동 입력

---

## 벡터화(임베딩)와 검색

- **임베딩 모델**: OpenAIEmbeddings 
- **문서/질문 벡터화**: 모든 문서와 사용자의 질문을 벡터로 변환
- **유사도 계산**: 코사인 유사도로 의미적으로 가장 가까운 문서 검색
- **RAG 구조**: 검색된 문서를 LLM에 컨텍스트로 넣어 더 정확한 답변 생성

---

## 데이터 흐름

1. **문서 수집**: FAQ, CSV, TXT, PDF 등 다양한 소스에서 데이터 로딩
2. **임베딩**: 모든 문서와 질문을 벡터로 변환
3. **검색**: 질문과 가장 유사한 문서 K개 추출
4. **LLM 답변**: 관련 문서와 함께 OpenAI GPT-3.5-turbo로 답변 생성
5. **프론트엔드 표시**: 답변, 추천 질문, 캐릭터 애니메이션 등 UI에 표시

---

## 기술 스택

- **백엔드**: Python, OpenAI API, Langchain, Pandas, PyPDF2, Numpy, dotenv
- **임베딩/검색**: OpenAIEmbeddings, 코사인 유사도, 벡터 기반 검색
- **프론트엔드**: HTML, CSS, JavaScript, Canvas, Bootstrap
- **데이터**: CSV, TXT, PDF 등 다양한 문서 포맷

---

## 배포
<img width="1583" alt="Screenshot 2025-05-12 at 6 59 15 AM" src="https://github.com/user-attachments/assets/61554f96-82b6-4196-93e9-5848454228b9" />

- **AWS Route 53**: 퍼블릭 도메인을 AWS DNS로 매핑
- **AWS Certificate Manager**: SSL 인증서 발급 후 확인 -> HTTPS 요청
- **AWS Elastic Beanstalk**: AWS S3, AWS ELB, AWS RDS, AWS Cloudwatch, EC2 instances, Auto Scaling 등의 서비스 연동을 자동화 


---

## 사용 예시

<img width="1172" alt="Screenshot 2025-05-12 at 5 47 24 AM" src="https://github.com/user-attachments/assets/f423fcd7-0b36-4314-b71a-a405b35a7f6f" />



<img width="1597" alt="Screenshot 2025-05-12 at 5 51 02 AM" src="https://github.com/user-attachments/assets/cda46b7e-55da-406b-97eb-9f1db8454190" />

- **실시간 질문**: "오늘 점심은 언제인가요?" → 관련 FAQ/문서 검색 후 LLM 답변
- **추천 질문**: "출결 확인 방법", "캠프 일정", "상담 신청" 등 랜덤 추천
- **캠퍼스 FAQ 제공**: 수강생들이 자주 묻는 질문들 정리


---

## 확장/개선 방향

- 벡터 DB(Pinecone, FAISS 등) 연동
- 사용자별 맞춤 추천 질문
- 대화 히스토리 기반 쿼리 강화
- 더 다양한 캐릭터/애니메이션 지원

---

## 참고

- [OpenAI Embeddings 공식 문서](https://platform.openai.com/docs/guides/embeddings)

---

## 회고

**박현준**: AWS와 웹 관련 기술에 대해 알아볼 수 있는 좋은 경험이었습니다. 팀원들께서 많이 도와주셔서 함께 알아가는 재미도 있었던 것 같습니다. 최종 프로젝트도 팀원들 모두 건승을 빕니다.

**편성민**:

**전서빈**:

**조영훈**:

**김재혁**:

