def writer_agent(results):
    summary = "# 📘 Research Report\n\n"

    for i, res in enumerate(results):
        summary += f"## 🔹 Point {i+1}\n"
        summary += f"{res}\n\n"

    summary += "---\n"
    summary += "✅ *End of Report*"

    return summary