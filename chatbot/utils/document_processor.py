from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def process_text(self, text):
        return self.text_splitter.split_text(text)

    def process_query(self, query, chat_history=None):
        # 이전 대화 맥락 고려
        if chat_history:
            context = self.get_context_from_history(chat_history)
            query = self.enhance_query_with_context(query, context)
        
