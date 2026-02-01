import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Get API key
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("❌ ERROR: GROQ_API_KEY not found in .env file")
    exit(1)

print("✅ API key loaded successfully")
print(f"   Key starts with: {groq_api_key[:10]}...")

# Test Groq connection
try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        
    )
    
    print("\n🔄 Testing Groq API connection...")
    response = llm.invoke("Say 'Hello from Jaisalmer!' in one sentence")
    
    print("✅ Groq API working!")
    print(f"\n🤖 Response: {response.content}")
    
    print("\n" + "="*50)
    print("🎉 ALL SYSTEMS GO! Setup completed successfully!")
    print("="*50)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print("Check your API key and internet connection")
