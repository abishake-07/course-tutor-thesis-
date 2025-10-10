from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import BudgetItem, BudgetCategory, User
from app.schemas import (
    BudgetItemCreate, BudgetItemUpdate, BudgetItem as BudgetItemSchema,
    BudgetCategoryCreate, BudgetCategory as BudgetCategorySchema,
    BudgetSummary
)
from app.services.auth import get_current_user

router = APIRouter()

# Budget Categories endpoints
@router.post("/categories/", response_model=BudgetCategorySchema)
async def create_budget_category(
    category: BudgetCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new budget category"""
    db_category = BudgetCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories/", response_model=List[BudgetCategorySchema])
async def get_budget_categories(
    db: Session = Depends(get_db)
):
    """Get all budget categories"""
    categories = db.query(BudgetCategory).all()
    return categories

# Budget Items endpoints
@router.post("/", response_model=BudgetItemSchema)
async def create_budget_item(
    budget_item: BudgetItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new budget item (income or expense)"""
    db_item = BudgetItem(
        **budget_item.dict(),
        owner_id=current_user.id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=List[BudgetItemSchema])
async def get_budget_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    transaction_type: Optional[str] = None,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's budget items with optional filtering"""
    query = db.query(BudgetItem).filter(BudgetItem.owner_id == current_user.id)
    
    if transaction_type:
        query = query.filter(BudgetItem.transaction_type == transaction_type)
    if category_id:
        query = query.filter(BudgetItem.category_id == category_id)
    if start_date:
        query = query.filter(BudgetItem.transaction_date >= start_date)
    if end_date:
        query = query.filter(BudgetItem.transaction_date <= end_date)
    
    items = query.order_by(BudgetItem.transaction_date.desc()).offset(skip).limit(limit).all()
    return items

@router.get("/summary", response_model=BudgetSummary)
async def get_budget_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get budget summary for the current user"""
    base_query = db.query(BudgetItem).filter(BudgetItem.owner_id == current_user.id)
    
    # Total income and expenses
    total_income = base_query.filter(BudgetItem.transaction_type == "income").with_entities(
        func.coalesce(func.sum(BudgetItem.amount), 0)
    ).scalar()
    
    total_expenses = base_query.filter(BudgetItem.transaction_type == "expense").with_entities(
        func.coalesce(func.sum(BudgetItem.amount), 0)
    ).scalar()
    
    # Current month data
    now = datetime.utcnow()
    current_month_query = base_query.filter(
        extract('year', BudgetItem.transaction_date) == now.year,
        extract('month', BudgetItem.transaction_date) == now.month
    )
    
    monthly_income = current_month_query.filter(BudgetItem.transaction_type == "income").with_entities(
        func.coalesce(func.sum(BudgetItem.amount), 0)
    ).scalar()
    
    monthly_expenses = current_month_query.filter(BudgetItem.transaction_type == "expense").with_entities(
        func.coalesce(func.sum(BudgetItem.amount), 0)
    ).scalar()
    
    # Categories summary
    categories_summary = db.query(
        BudgetCategory.name,
        BudgetCategory.color,
        func.coalesce(func.sum(BudgetItem.amount), 0).label("total_amount")
    ).join(
        BudgetItem, BudgetCategory.id == BudgetItem.category_id, isouter=True
    ).filter(
        BudgetItem.owner_id == current_user.id,
        BudgetItem.transaction_type == "expense"
    ).group_by(BudgetCategory.id, BudgetCategory.name, BudgetCategory.color).all()
    
    categories_list = [
        {
            "name": cat.name,
            "color": cat.color,
            "amount": float(cat.total_amount)
        } for cat in categories_summary
    ]
    
    return BudgetSummary(
        total_income=float(total_income or 0),
        total_expenses=float(total_expenses or 0),
        net_balance=float((total_income or 0) - (total_expenses or 0)),
        monthly_income=float(monthly_income or 0),
        monthly_expenses=float(monthly_expenses or 0),
        categories_summary=categories_list
    )

@router.get("/{item_id}", response_model=BudgetItemSchema)
async def get_budget_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific budget item"""
    item = db.query(BudgetItem).filter(
        BudgetItem.id == item_id,
        BudgetItem.owner_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    
    return item

@router.put("/{item_id}", response_model=BudgetItemSchema)
async def update_budget_item(
    item_id: int,
    item_update: BudgetItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a budget item"""
    db_item = db.query(BudgetItem).filter(
        BudgetItem.id == item_id,
        BudgetItem.owner_id == current_user.id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    
    update_data = item_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def delete_budget_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a budget item"""
    db_item = db.query(BudgetItem).filter(
        BudgetItem.id == item_id,
        BudgetItem.owner_id == current_user.id
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Budget item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Budget item deleted successfully"}

@router.get("/analytics/monthly", response_model=List[dict])
async def get_monthly_analytics(
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly budget analytics for the specified number of months"""
    now = datetime.utcnow()
    start_date = now - timedelta(days=months * 30)
    
    monthly_data = db.query(
        extract('year', BudgetItem.transaction_date).label('year'),
        extract('month', BudgetItem.transaction_date).label('month'),
        BudgetItem.transaction_type,
        func.sum(BudgetItem.amount).label('total_amount')
    ).filter(
        BudgetItem.owner_id == current_user.id,
        BudgetItem.transaction_date >= start_date
    ).group_by(
        extract('year', BudgetItem.transaction_date),
        extract('month', BudgetItem.transaction_date),
        BudgetItem.transaction_type
    ).all()
    
    # Organize data by month
    monthly_summary = {}
    for data in monthly_data:
        month_key = f"{int(data.year)}-{int(data.month):02d}"
        if month_key not in monthly_summary:
            monthly_summary[month_key] = {"income": 0, "expenses": 0}
        
        monthly_summary[month_key][data.transaction_type + "s" if data.transaction_type == "expense" else data.transaction_type] = float(data.total_amount)
    
    # Convert to sorted list
    result = []
    for month_key in sorted(monthly_summary.keys()):
        data = monthly_summary[month_key]
        result.append({
            "month": month_key,
            "income": data["income"],
            "expenses": data["expenses"],
            "net": data["income"] - data["expenses"]
        })
    
    return result