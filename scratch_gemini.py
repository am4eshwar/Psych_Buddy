import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

async def test_tool_call():
    def get_weather_sync(location: str) -> str:
        """Get the weather for a location."""
        import threading
        print(f"Tool thread: {threading.current_thread().name}")
        try:
            loop = asyncio.get_running_loop()
            print(f"Tool loop running: {loop.is_running()}")
        except RuntimeError:
            print("No running loop in tool thread.")
        return f"The weather in {location} is sunny."
        
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        tools=[get_weather_sync]
    )
    
    chat = model.start_chat(enable_automatic_function_calling=True)
    print("Sending message...")
    response = await chat.send_message_async("What is the weather in London?")
    
    print("Response parts:")
    for part in response.parts:
        if part.function_call:
            print("Function call found!")
            print(f"Name: {part.function_call.name}")
            print(f"Args: {dict(part.function_call.args)}")
            
            # test responding
            func_response = [{
                "function_response": {
                    "name": part.function_call.name,
                    "response": {"result": "The weather in London is rainy"}
                }
            }]
            print("Sending function response...")
            response2 = await chat.send_message_async(func_response)
            print(f"Final text: {response2.text}")

if __name__ == "__main__":
    asyncio.run(test_tool_call())
