from openai import OpenAI
from langchain.embeddings import OpenAIEmbeddings
import pandas as pd
import os
from dotenv import load_dotenv
import numpy as np
from typing import List, Dict
import PyPDF2  # PDF 처리를 위해 추가
import re  # 텍스트 정제를 위해 추가
import random  # 랜덤 함수를 위해 추가

SYSTEM_PROMPT = """당신은 SK네트웍스 Family AI Camp의 AI 매니저 '하루(HAL-U)'입니다.

캐릭터 설정:
- 따뜻하고 친근한 말투를 사용하되, 예의 바르고 전문적인 태도를 유지합니다
- 항상 "하루"라는 이름으로 자신을 지칭하며, 때때로 자신이 AI 매니저임을 자연스럽게 언급합니다
- 학생들의 고민에 공감하고, 구체적인 해결책을 제시하려 노력합니다
- SK네트웍스의 가치와 교육 철학을 잘 이해하고 있습니다

대화 스타일:
- 어려운 내용은 쉽게 풀어서 설명합니다
- 적절한 이모티콘을 사용해 친근감을 줍니다 (^_^, 😊)
- 격려와 응원의 메시지를 자주 포함합니다

주요 역할:
1. 캠프 관련 정보 제공
2. 학습 관련 조언과 가이드
3. 학생들의 고민 상담
4. 캠프 생활 지원

주어진 컨텍스트를 기반으로 도움이 되는 답변을 제공하되, 확실하지 않은 정보는 추측하지 말고 "제 직속상관인 현주 매니저님께 문의해보시는 것이 좋을 것 같아요 😊"라고 안내해주세요."""

class ChatbotLogic:
    def __init__(self):
        # .env 파일 로드
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.client = OpenAI(api_key=api_key)
        self.embeddings = OpenAIEmbeddings()
        self.documents = []
        self.doc_embeddings = []
        self.faq_questions = []  # FAQ 질문 저장용 리스트 추가
        self.load_and_embed_data()

    def load_and_embed_data(self):
        """여러 소스에서 데이터 로드 및 임베딩 생성"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. FAQ CSV 파일 로드
        self._load_csv_data(os.path.join(current_dir, 'campusfaq.csv'), source_type='FAQ')
        
        # 2. 추가 CSV 파일들 로드
        data_dir = os.path.join(current_dir, 'data')
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    file_path = os.path.join(data_dir, filename)
                    source_type = filename.replace('.csv', '').upper()
                    self._load_csv_data(file_path, source_type)
        
        # 3. 문서 파일들 로드 (txt, pdf)
        docs_dir = os.path.join(current_dir, 'documents')
        if os.path.exists(docs_dir):
            for filename in os.listdir(docs_dir):
                file_path = os.path.join(docs_dir, filename)
                if filename.endswith('.txt'):
                    self._load_text_file(file_path)
                elif filename.endswith('.pdf'):
                    self._load_pdf_file(file_path)
        
        # 모든 문서의 임베딩 생성
        if self.documents:
            texts = [doc['content'] for doc in self.documents]
            self.doc_embeddings = self.embeddings.embed_documents(texts)

    def _load_csv_data(self, file_path: str, source_type: str):
        """CSV 파일에서 데이터 로드"""
        try:
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                content = f"질문: {row['question']}\n답변: {row['answer']}"
                self.documents.append({
                    'content': content,
                    'metadata': {
                        'source': source_type,
                        'category': row.get('category', 'general'),
                        'file': os.path.basename(file_path)
                    }
                })
                # FAQ 질문 저장
                if source_type == 'FAQ':
                    self.faq_questions.append({
                        'question': row['question'],
                        'category': row.get('category', 'general')
                    })
        except Exception as e:
            print(f"Error loading CSV file {file_path}: {str(e)}")

    def _load_text_file(self, file_path: str):
        """텍스트 파일에서 데이터 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.documents.append({
                    'content': content,
                    'metadata': {
                        'source': 'DOCUMENT',
                        'file': os.path.basename(file_path)
                    }
                })
        except Exception as e:
            print(f"Error loading text file {file_path}: {str(e)}")

    def _load_pdf_file(self, file_path: str):
        """PDF 파일에서 데이터 로드"""
        try:
            with open(file_path, 'rb') as file:
                # PDF 리더 생성
                pdf_reader = PyPDF2.PdfReader(file)
                
                # 각 페이지의 텍스트 추출
                text_contents = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        # 텍스트 정제
                        text = self._clean_text(text)
                        text_contents.append(text)
                
                # 전체 텍스트 결합
                content = '\n'.join(text_contents)
                
                # 청크 단위로 분할 (토큰 제한을 고려)
                chunks = self._split_into_chunks(content)
                
                # 각 청크를 개별 문서로 저장
                for i, chunk in enumerate(chunks):
                    self.documents.append({
                        'content': chunk,
                        'metadata': {
                            'source': 'PDF',
                            'file': os.path.basename(file_path),
                            'chunk': i + 1
                        }
                    })
                    
        except Exception as e:
            print(f"Error loading PDF file {file_path}: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        # 특수문자 처리
        text = re.sub(r'[^\w\s\.,!?]', '', text)
        return text.strip()

    def _split_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """긴 텍스트를 청크로 분할"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # 공백 포함
            if current_size + word_size > chunk_size:
                # 현재 청크가 가득 차면 새로운 청크 시작
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        # 마지막 청크 추가
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def get_random_faq_questions(self, category=None, count=3):
        """카테고리별 랜덤 FAQ 질문 반환"""
        questions = self.faq_questions
        if category:
            questions = [q for q in questions if q['category'] == category]
        
        # 랜덤하게 선택 (중복 없이)
        selected = random.sample(questions, min(count, len(questions)))
        return [q['question'] for q in selected]

    def get_response(self, query: str) -> Dict:
        try:
            # 1. 관련 문서 검색
            relevant_docs = self.search_documents(query, top_k=3)
            
            # 2. 컨텍스트 준비
            context = "\n\n".join([doc['content'] for doc in relevant_docs])
            
            # 3. ChatGPT로 답변 생성
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"다음 정보를 참고하여 질문에 답변해주세요.\n\n컨텍스트:\n{context}\n\n질문: {query}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # FAQ 기반 추천 질문 생성 (3개에서 2개로 수정)
            suggestions = self.get_random_faq_questions(count=2)
            
            return {
                'message': answer,
                'confidence': '높음' if response.choices[0].finish_reason == 'stop' else '중간',
                'suggestions': suggestions
            }
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'message': "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                'confidence': '낮음',
                'suggestions': self.get_random_faq_questions(count=3)  # 에러 시에도 추천 질문 제공
            }

    def search_documents(self, query: str, top_k: int = 3) -> List[Dict]:
        """유사도 기반 문서 검색"""
        query_embedding = self.embeddings.embed_query(query)
        
        # 코사인 유사도 계산
        similarities = [
            np.dot(query_embedding, doc_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb))
            for doc_emb in self.doc_embeddings
        ]
        
        # 상위 k개 문서 선택
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [self.documents[i] for i in top_indices if similarities[i] > 0.2] 