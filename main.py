from app.graph.workflow import run_workflow

def main():
    query = input("Enter your research topic: ")
    result = run_workflow(query)
    print("\n--- OUTPUT ---\n")
    print(result)

if __name__ == "__main__":
    main()