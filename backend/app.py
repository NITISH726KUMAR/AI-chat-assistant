from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import json
from dotenv import load_dotenv

from database import get_db, ChatMessage, create_tables

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is missing or default placeholder
if not api_key or api_key == "your-actual-openai-api-key-here":
    print("WARNING: OpenAI API key is not set. Please set OPENAI_API_KEY in your .env file")
else:
    # Initialize OpenAI client
    openai.api_key = api_key

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
create_tables()

class MessageRequest(BaseModel):
    message: str
    conversation_id: str = None

class MessageResponse(BaseModel):
    response: str
    conversation_id: str

@app.get("/")
def read_root():
    return {"message": "AI Chat Assistant API"}

@app.post("/api/chat", response_model=MessageResponse)
async def chat(request: MessageRequest, db: Session = Depends(get_db)):
    try:
        if not api_key or api_key == "your-actual-openai-api-key-here":
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file"
            )

        # Store user message
        user_message = ChatMessage(
            conversation_id=request.conversation_id,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()

        # Get conversation history if conversation_id exists
        messages = []
        if request.conversation_id:
            history = db.query(ChatMessage).filter(
                ChatMessage.conversation_id == request.conversation_id
            ).order_by(ChatMessage.timestamp.asc()).all()
            
            messages = [{"role": msg.role, "content": msg.content} for msg in history]
        else:
            # Create system message for new conversations
            messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
            messages.append({"role": "user", "content": request.message})
        
        try:
            # Generate response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            ai_response = response.choices[0].message.content
            conversation_id = request.conversation_id or user_message.conversation_id
        except Exception as openai_error:
            print(f"OpenAI API Error: {str(openai_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error communicating with OpenAI API: {str(openai_error)}"
            )
        
        # Store AI response
        ai_message = ChatMessage(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        db.add(ai_message)
        db.commit()
        
        return {"response": ai_response, "conversation_id": conversation_id}
    
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    
    try:
        if not api_key or api_key == "your-actual-openai-api-key-here":
            await websocket.send_json({
                "error": "OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file"
            })
            await websocket.close()
            return

        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            
            user_message = data.get("message")
            conversation_id = data.get("conversation_id")
            
            chat_msg = ChatMessage(
                conversation_id=conversation_id,
                role="user",
                content=user_message
            )
            db.add(chat_msg)
            db.commit()
            
            messages = []
            if conversation_id:
                history = db.query(ChatMessage).filter(
                    ChatMessage.conversation_id == conversation_id
                ).order_by(ChatMessage.timestamp.asc()).all()
                
                messages = [{"role": msg.role, "content": msg.content} for msg in history]
            else:
                messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
                messages.append({"role": "user", "content": user_message})
            
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages
                )
                
                ai_response = response.choices[0].message.content
                conversation_id = conversation_id or chat_msg.conversation_id
            except Exception as openai_error:
                print(f"OpenAI API Error: {str(openai_error)}")
                await websocket.send_json({
                    "error": f"Error communicating with OpenAI API: {str(openai_error)}"
                })
                continue
            
            ai_message = ChatMessage(
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response
            )
            db.add(ai_message)
            db.commit()
            
            await websocket.send_json({
                "response": ai_response,
                "conversation_id": conversation_id
            })
            
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()

@app.get("/api/conversations/{conversation_id}", response_model=List[dict])
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.timestamp.asc()).all()
    
    return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 