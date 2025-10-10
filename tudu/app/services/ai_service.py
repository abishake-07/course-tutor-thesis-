import openai
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Task, BudgetItem, BudgetCategory
import speech_recognition as sr
from io import BytesIO
import base64

class AIService:
    def __init__(self):
        self.openai_client = None
        self.setup_openai()
        
    def setup_openai(self):
        """Initialize OpenAI client if API key is available"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai.api_key = api_key
            self.openai_client = openai
    
    async def process_voice_command(self, command: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Process voice commands and execute corresponding actions"""
        command_lower = command.lower()
        
        # Task-related commands
        if any(keyword in command_lower for keyword in ["add task", "create task", "new task"]):
            return await self._handle_add_task_command(command, user_id, db)
        
        elif any(keyword in command_lower for keyword in ["complete task", "finish task", "mark done"]):
            return await self._handle_complete_task_command(command, user_id, db)
        
        elif any(keyword in command_lower for keyword in ["show tasks", "list tasks", "my tasks"]):
            return await self._handle_show_tasks_command(user_id, db)
        
        # Budget-related commands
        elif any(keyword in command_lower for keyword in ["add expense", "spent", "bought"]):
            return await self._handle_add_expense_command(command, user_id, db)
        
        elif any(keyword in command_lower for keyword in ["add income", "earned", "received"]):
            return await self._handle_add_income_command(command, user_id, db)
        
        elif any(keyword in command_lower for keyword in ["budget summary", "spending", "expenses"]):
            return await self._handle_budget_summary_command(user_id, db)
        
        else:
            return {
                "message": "I didn't understand that command. Try saying 'add task', 'show tasks', 'add expense', or 'budget summary'.",
                "action": None
            }
    
    async def _handle_add_task_command(self, command: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Extract task details from voice command and create task"""
        try:
            # Use regex to extract task title (simple implementation)
            # More sophisticated NLP could be used here
            task_match = re.search(r'(?:add task|create task|new task)[\s:]*(.*)', command, re.IGNORECASE)
            if task_match:
                task_title = task_match.group(1).strip()
                
                # Extract priority if mentioned
                priority = "medium"
                if any(word in command.lower() for word in ["urgent", "high priority"]):
                    priority = "urgent"
                elif "high" in command.lower():
                    priority = "high"
                elif "low" in command.lower():
                    priority = "low"
                
                # Create task
                new_task = Task(
                    title=task_title,
                    priority=priority,
                    owner_id=user_id
                )
                db.add(new_task)
                db.commit()
                
                return {
                    "message": f"Task '{task_title}' added successfully with {priority} priority.",
                    "action": "task_added",
                    "data": {"task_id": new_task.id, "title": task_title}
                }
            else:
                return {
                    "message": "Please specify the task title. For example: 'Add task: Buy groceries'",
                    "action": None
                }
        except Exception as e:
            return {
                "message": f"Error creating task: {str(e)}",
                "action": None
            }
    
    async def _handle_complete_task_command(self, command: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Mark a task as completed based on voice command"""
        try:
            # Get user's pending tasks
            pending_tasks = db.query(Task).filter(
                Task.owner_id == user_id,
                Task.status.in_(["pending", "in_progress"])
            ).all()
            
            if not pending_tasks:
                return {
                    "message": "You don't have any pending tasks to complete.",
                    "action": None
                }
            
            # Simple approach: complete the first pending task
            # More sophisticated matching could be implemented
            task_to_complete = pending_tasks[0]
            task_to_complete.status = "completed"
            task_to_complete.completed_at = datetime.utcnow()
            db.commit()
            
            return {
                "message": f"Task '{task_to_complete.title}' marked as completed.",
                "action": "task_completed",
                "data": {"task_id": task_to_complete.id}
            }
        except Exception as e:
            return {
                "message": f"Error completing task: {str(e)}",
                "action": None
            }
    
    async def _handle_show_tasks_command(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get summary of user's tasks"""
        try:
            pending_tasks = db.query(Task).filter(
                Task.owner_id == user_id,
                Task.status == "pending"
            ).count()
            
            in_progress_tasks = db.query(Task).filter(
                Task.owner_id == user_id,
                Task.status == "in_progress"
            ).count()
            
            # Get overdue tasks
            overdue_tasks = db.query(Task).filter(
                Task.owner_id == user_id,
                Task.due_date < datetime.utcnow(),
                Task.status.in_(["pending", "in_progress"])
            ).count()
            
            message = f"You have {pending_tasks} pending tasks, {in_progress_tasks} in progress"
            if overdue_tasks > 0:
                message += f", and {overdue_tasks} overdue tasks"
            message += "."
            
            return {
                "message": message,
                "action": "tasks_summarized",
                "data": {
                    "pending": pending_tasks,
                    "in_progress": in_progress_tasks,
                    "overdue": overdue_tasks
                }
            }
        except Exception as e:
            return {
                "message": f"Error getting tasks: {str(e)}",
                "action": None
            }
    
    async def _handle_add_expense_command(self, command: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Add expense from voice command"""
        try:
            # Extract amount using regex
            amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', command)
            if not amount_match:
                return {
                    "message": "Please specify the amount. For example: 'I spent $25 on lunch'",
                    "action": None
                }
            
            amount = float(amount_match.group(1))
            
            # Extract description (simple implementation)
            description = command.replace(amount_match.group(0), "").strip()
            description = re.sub(r'(add expense|spent|bought|on)', '', description, flags=re.IGNORECASE).strip()
            
            if not description:
                description = "Voice expense"
            
            # Create budget item
            expense = BudgetItem(
                title=description,
                amount=amount,
                transaction_type="expense",
                owner_id=user_id
            )
            db.add(expense)
            db.commit()
            
            return {
                "message": f"Expense of ${amount:.2f} for '{description}' added successfully.",
                "action": "expense_added",
                "data": {"amount": amount, "description": description}
            }
        except Exception as e:
            return {
                "message": f"Error adding expense: {str(e)}",
                "action": None
            }
    
    async def _handle_add_income_command(self, command: str, user_id: int, db: Session) -> Dict[str, Any]:
        """Add income from voice command"""
        try:
            # Extract amount using regex
            amount_match = re.search(r'\$?(\d+(?:\.\d{2})?)', command)
            if not amount_match:
                return {
                    "message": "Please specify the amount. For example: 'I earned $500 from freelancing'",
                    "action": None
                }
            
            amount = float(amount_match.group(1))
            
            # Extract description
            description = command.replace(amount_match.group(0), "").strip()
            description = re.sub(r'(add income|earned|received|from)', '', description, flags=re.IGNORECASE).strip()
            
            if not description:
                description = "Voice income"
            
            # Create budget item
            income = BudgetItem(
                title=description,
                amount=amount,
                transaction_type="income",
                owner_id=user_id
            )
            db.add(income)
            db.commit()
            
            return {
                "message": f"Income of ${amount:.2f} from '{description}' added successfully.",
                "action": "income_added",
                "data": {"amount": amount, "description": description}
            }
        except Exception as e:
            return {
                "message": f"Error adding income: {str(e)}",
                "action": None
            }
    
    async def _handle_budget_summary_command(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get budget summary"""
        try:
            # Calculate monthly totals
            now = datetime.utcnow()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_income = db.query(func.sum(BudgetItem.amount)).filter(
                BudgetItem.owner_id == user_id,
                BudgetItem.transaction_type == "income",
                BudgetItem.transaction_date >= start_of_month
            ).scalar() or 0
            
            monthly_expenses = db.query(func.sum(BudgetItem.amount)).filter(
                BudgetItem.owner_id == user_id,
                BudgetItem.transaction_type == "expense",
                BudgetItem.transaction_date >= start_of_month
            ).scalar() or 0
            
            net_balance = monthly_income - monthly_expenses
            
            message = f"This month you've earned ${monthly_income:.2f} and spent ${monthly_expenses:.2f}. "
            if net_balance > 0:
                message += f"You're ahead by ${net_balance:.2f}!"
            elif net_balance < 0:
                message += f"You're over budget by ${abs(net_balance):.2f}."
            else:
                message += "You're breaking even."
            
            return {
                "message": message,
                "action": "budget_summarized",
                "data": {
                    "monthly_income": monthly_income,
                    "monthly_expenses": monthly_expenses,
                    "net_balance": net_balance
                }
            }
        except Exception as e:
            return {
                "message": f"Error getting budget summary: {str(e)}",
                "action": None
            }
    
    async def generate_insights(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Generate AI insights about user's tasks and budget"""
        insights = []
        
        try:
            # Task insights
            task_insights = await self._generate_task_insights(user_id, db)
            insights.extend(task_insights)
            
            # Budget insights
            budget_insights = await self._generate_budget_insights(user_id, db)
            insights.extend(budget_insights)
            
            # Goal insights
            goal_insights = await self._generate_goal_insights(user_id, db)
            insights.extend(goal_insights)
            
        except Exception as e:
            # Return fallback insights if AI fails
            insights = self._get_fallback_insights()
        
        return insights
    
    async def _generate_task_insights(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Generate task-related insights"""
        insights = []
        
        # Count overdue tasks
        overdue_count = db.query(Task).filter(
            Task.owner_id == user_id,
            Task.due_date < datetime.utcnow(),
            Task.status.in_(["pending", "in_progress"])
        ).count()
        
        if overdue_count > 0:
            insights.append({
                "title": "Overdue Tasks",
                "message": f"You have {overdue_count} overdue task{'s' if overdue_count > 1 else ''}. Consider rescheduling or breaking them into smaller tasks.",
                "icon": "fas fa-exclamation-triangle",
                "type": "warning"
            })
        
        # Check high priority tasks
        high_priority_count = db.query(Task).filter(
            Task.owner_id == user_id,
            Task.priority.in_(["high", "urgent"]),
            Task.status.in_(["pending", "in_progress"])
        ).count()
        
        if high_priority_count > 0:
            insights.append({
                "title": "High Priority Focus",
                "message": f"You have {high_priority_count} high-priority task{'s' if high_priority_count > 1 else ''}. Focus on these first!",
                "icon": "fas fa-star",
                "type": "info"
            })
        
        return insights
    
    async def _generate_budget_insights(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Generate budget-related insights"""
        insights = []
        
        # Compare current month to previous month
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
        
        current_expenses = db.query(func.sum(BudgetItem.amount)).filter(
            BudgetItem.owner_id == user_id,
            BudgetItem.transaction_type == "expense",
            BudgetItem.transaction_date >= current_month_start
        ).scalar() or 0
        
        prev_expenses = db.query(func.sum(BudgetItem.amount)).filter(
            BudgetItem.owner_id == user_id,
            BudgetItem.transaction_type == "expense",
            BudgetItem.transaction_date >= prev_month_start,
            BudgetItem.transaction_date < current_month_start
        ).scalar() or 0
        
        if prev_expenses > 0:
            change_percent = ((current_expenses - prev_expenses) / prev_expenses) * 100
            if abs(change_percent) > 10:
                direction = "increased" if change_percent > 0 else "decreased"
                insights.append({
                    "title": "Spending Trend",
                    "message": f"Your expenses have {direction} by {abs(change_percent):.1f}% compared to last month.",
                    "icon": "fas fa-chart-line",
                    "type": "info" if change_percent < 0 else "warning"
                })
        
        return insights
    
    async def _generate_goal_insights(self, user_id: int, db: Session) -> List[Dict[str, Any]]:
        """Generate goal-related insights"""
        insights = []
        
        # Calculate completion rate
        total_tasks = db.query(Task).filter(Task.owner_id == user_id).count()
        completed_tasks = db.query(Task).filter(
            Task.owner_id == user_id,
            Task.status == "completed"
        ).count()
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            if completion_rate >= 80:
                insights.append({
                    "title": "Great Progress!",
                    "message": f"You've completed {completion_rate:.0f}% of your tasks. Keep up the excellent work!",
                    "icon": "fas fa-trophy",
                    "type": "success"
                })
        
        return insights
    
    def _get_fallback_insights(self) -> List[Dict[str, Any]]:
        """Fallback insights when AI is not available"""
        return [
            {
                "title": "Stay Organized",
                "message": "Regular task review helps maintain productivity. Consider setting aside 15 minutes daily for planning.",
                "icon": "fas fa-lightbulb",
                "type": "info"
            },
            {
                "title": "Budget Tracking",
                "message": "Consistent expense tracking is key to financial health. Try to log expenses daily.",
                "icon": "fas fa-chart-pie",
                "type": "info"
            }
        ]
    
    async def suggest_task_breakdown(self, task: Task) -> List[str]:
        """Suggest ways to break down a complex task"""
        if self.openai_client and os.getenv("OPENAI_API_KEY"):
            try:
                prompt = f"""
                Break down this task into smaller, actionable subtasks:
                Title: {task.title}
                Description: {task.description or 'No description'}
                
                Provide 3-5 specific, actionable subtasks that would help complete this main task.
                Return as a simple list, one item per line.
                """
                
                response = await self.openai_client.ChatCompletion.acreate(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                
                suggestions = response.choices[0].message.content.strip().split('\n')
                return [s.strip('- ').strip() for s in suggestions if s.strip()]
            except:
                pass
        
        # Fallback suggestions
        return [
            f"Research requirements for '{task.title}'",
            f"Create a plan for '{task.title}'",
            f"Gather necessary resources",
            f"Execute main work",
            f"Review and finalize '{task.title}'"
        ]
    
    async def categorize_expense(self, title: str, description: str = "") -> str:
        """Categorize an expense using AI"""
        # Simple rule-based categorization (can be enhanced with ML)
        title_lower = title.lower()
        desc_lower = description.lower()
        text = f"{title_lower} {desc_lower}"
        
        if any(word in text for word in ["food", "restaurant", "lunch", "dinner", "grocery", "supermarket"]):
            return "Food & Dining"
        elif any(word in text for word in ["gas", "fuel", "car", "uber", "taxi", "transport"]):
            return "Transportation"
        elif any(word in text for word in ["movie", "entertainment", "game", "concert", "show"]):
            return "Entertainment"
        elif any(word in text for word in ["clothes", "shopping", "store", "mall", "amazon"]):
            return "Shopping"
        elif any(word in text for word in ["rent", "mortgage", "utilities", "electric", "water", "internet"]):
            return "Bills & Utilities"
        elif any(word in text for word in ["doctor", "medicine", "pharmacy", "hospital", "health"]):
            return "Healthcare"
        else:
            return "Other"
    
    async def analyze_budget_patterns(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Analyze spending patterns and provide insights"""
        # Get spending by category for current month
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        category_spending = db.query(
            BudgetCategory.name,
            func.sum(BudgetItem.amount).label("total")
        ).join(
            BudgetItem, BudgetCategory.id == BudgetItem.category_id
        ).filter(
            BudgetItem.owner_id == user_id,
            BudgetItem.transaction_type == "expense",
            BudgetItem.transaction_date >= start_of_month
        ).group_by(BudgetCategory.name).all()
        
        # Find top spending category
        if category_spending:
            top_category = max(category_spending, key=lambda x: x.total)
            
            analysis = {
                "top_spending_category": {
                    "name": top_category.name,
                    "amount": float(top_category.total),
                    "percentage": 0  # Calculate if needed
                },
                "recommendations": [
                    f"Your highest spending is in {top_category.name}. Consider setting a monthly limit.",
                    "Track daily expenses to stay within budget.",
                    "Look for opportunities to reduce costs in your top spending categories."
                ]
            }
        else:
            analysis = {
                "message": "Not enough spending data to analyze patterns yet.",
                "recommendations": [
                    "Start tracking your expenses to get personalized insights.",
                    "Categorize your transactions for better analysis."
                ]
            }
        
        return analysis