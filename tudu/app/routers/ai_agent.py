from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Task, BudgetItem, AIInteraction
from app.schemas import VoiceCommand, VoiceResponse
from app.services.auth import get_current_user
from app.services.ai_service import AIService
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict

router = APIRouter()

@router.post("/voice-command", response_model=VoiceResponse)
async def process_voice_command(
    command: VoiceCommand,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process voice commands using AI"""
    try:
        ai_service = AIService()
        
        # Log the interaction
        interaction = AIInteraction(
            user_id=current_user.id,
            interaction_type="voice",
            user_input=command.command
        )
        
        # Process the command
        result = await ai_service.process_voice_command(command.command, current_user.id, db)
        
        # Update interaction with response
        interaction.ai_response = result["message"]
        interaction.context_data = json.dumps(result.get("data", {}))
        
        db.add(interaction)
        db.commit()
        
        return VoiceResponse(
            success=True,
            message=result["message"],
            action_performed=result.get("action"),
            data=result.get("data")
        )
        
    except Exception as e:
        return VoiceResponse(
            success=False,
            message=f"Sorry, I couldn't process that command: {str(e)}"
        )

@router.get("/insights")
async def get_ai_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-generated insights about tasks and budget"""
    try:
        ai_service = AIService()
        insights = await ai_service.generate_insights(current_user.id, db)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-task-breakdown/{task_id}")
async def suggest_task_breakdown(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI suggestions for breaking down a complex task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.owner_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        ai_service = AIService()
        suggestions = await ai_service.suggest_task_breakdown(task)
        
        # Update task with AI suggestions
        task.ai_suggestions = json.dumps(suggestions)
        db.commit()
        
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/categorize-expense")
async def categorize_expense(
    title: str,
    description: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI-powered expense categorization"""
    try:
        ai_service = AIService()
        category = await ai_service.categorize_expense(title, description)
        return {"suggested_category": category}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget-analysis")
async def get_budget_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI analysis of spending patterns"""
    try:
        ai_service = AIService()
        analysis = await ai_service.analyze_budget_patterns(current_user.id, db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))