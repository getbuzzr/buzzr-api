from fastapi import APIRouter, HTTPException, Depends, status
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
# Models
from models.Department import Department
# Auth
from auth import get_current_user
from utils import serialize
# utils
from database import get_db

router = APIRouter()
