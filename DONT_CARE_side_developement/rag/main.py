import time

from rag_optimized import RAG


def main():
    start_time = time.time()

    rag = RAG()
    
    # Load documents
    pdf_path = r"rag\data\Book1.pdf"
    # pdf_path = r"rag\data\Learning_algos.pdf"
    
    try:
        # Load documents (this is where the time will be spent)
        result = rag.load_documents(pdf_path)
        
        # Example query
        if rag.is_initialized:
            while True:
                custom_query = ""
                question = custom_query if custom_query else input("User: ")
                if question in ["q", "exit", "quit"]:
                    break

                response = rag.query(question)


                if isinstance(response, dict):
                    print(f"\nAnswer: {response.get('answer', 'No answer found')}")
                    if 'context' in response:
                        print(f"Used {len(response['context'])} source documents")
                else:
                    print(f"\nAnswer: {response}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    total_time = time.time() - start_time
    print(f"\nTotal execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main()