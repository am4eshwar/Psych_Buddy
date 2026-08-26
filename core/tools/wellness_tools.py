"""
Wellness and Planning tools for the ReAct architecture.
Provides functions for creating wellness plans, fetching coping strategies, and tracking tasks.
"""
from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone, timedelta
from loguru import logger
import json

from utils.coping_strategies import get_coping_strategies
from models.task import WellnessTask, TaskType, TaskStatus, TaskPriority


def get_wellness_tools(memory_manager, user_id: str, scheduler=None):
    """
    Factory function to return wellness and planning tools bound to the current user
    and memory manager. These functions expose clear schemas for the LLM.
    """

    async def fetch_coping_strategies(mental_state: str) -> Dict[str, List[str]]:
        """
        Retrieves therapeutic coping strategies from the database based on the diagnosed mental state.
        Call this when you need evidence-based exercises or strategies for the user's current condition.
        
        Args:
            mental_state: The primary mental state (e.g., 'anxiety', 'sadness', 'anger', 'stress', 'loneliness').
        """
        logger.info(f"LLM Tool Call: fetch_coping_strategies for {mental_state} ({user_id})")
        # In a real system, intensity could be passed or determined dynamically
        strategies = get_coping_strategies(mental_state, intensity='moderate')
        return strategies

    async def save_wellness_plan(tasks: List[Dict[str, Any]]) -> str:
        """
        Saves the proposed daily tasks to PostgreSQL so the scheduler can pick them up later.
        Call this after generating a wellness plan with the user.
        
        Args:
            tasks: A list of task dictionaries. Each dictionary should have the following keys:
                   - 'title' (str): Short title of the task
                   - 'description' (str): Short description
                   - 'instructions' (str): Detailed instructions
                   - 'task_type' (str): e.g., 'breathing_exercise', 'mindfulness', 'journaling'
                   - 'scheduled_time' (str): ISO formatted datetime string (e.g., '2023-10-15T09:00:00Z')
                   - 'duration_minutes' (int): Duration of the task in minutes
        """
        logger.info(f"LLM Tool Call: save_wellness_plan for {user_id}")
        session = await memory_manager.get_active_session(user_id)
        if not session:
            return "Failed to save wellness plan: No active session found."

        saved_count = 0
        for task_dict in tasks:
            try:
                # Convert string task_type to TaskType enum if possible, or fallback
                task_type_str = task_dict.get('task_type', 'self_care').upper()
                try:
                    task_type = TaskType[task_type_str]
                except KeyError:
                    task_type = TaskType.SELF_CARE

                # Parse scheduled time
                time_str = task_dict.get('scheduled_time')
                if time_str:
                    try:
                        scheduled_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    except ValueError:
                        scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
                else:
                    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)

                task = WellnessTask(
                    task_id=str(uuid.uuid4()),
                    session_id=session.session_id,
                    user_id=user_id,
                    task_type=task_type,
                    title=task_dict.get('title', 'Wellness Task'),
                    description=task_dict.get('description', ''),
                    instructions=task_dict.get('instructions', ''),
                    scheduled_time=scheduled_time,
                    duration_minutes=int(task_dict.get('duration_minutes', 15)),
                    priority=TaskPriority.MEDIUM,
                    status=TaskStatus.PENDING
                )
                await memory_manager.save_task(task)
                saved_count += 1
            except Exception as e:
                logger.error(f"Failed to parse and save task: {e}")

        return f"Successfully saved {saved_count} wellness tasks to the database."

    async def get_todays_tasks() -> List[Dict[str, Any]]:
        """
        Retrieves what the user is supposed to be doing today (today's tasks + overdue items).
        Call this to check the user's schedule so you can ask them about it or remind them.
        """
        logger.info(f"LLM Tool Call: get_todays_tasks for {user_id}")
        tasks = await memory_manager.get_todays_tasks(user_id)
        return tasks

    async def mark_task_completed(task_id: str) -> str:
        """
        Updates a specific task in the database as completed when the user confirms they did it.
        Call this when the user says they have finished a scheduled task.
        
        Args:
            task_id: The unique identifier of the task to mark as completed.
        """
        logger.info(f"LLM Tool Call: mark_task_completed for {task_id} ({user_id})")
        success = await memory_manager.update_task_status(task_id, "completed", user_id=user_id)
        if success:
            return f"Task {task_id} successfully marked as completed."
        return f"Failed to mark task {task_id} as completed. Task not found or error occurred."

    async def schedule_program(preferences: Dict[str, Any]) -> str:
        """
        Schedules the 28-day check-in program for a new user.
        You MUST call this tool when you assess a new user's initial state to set up their daily check-ins.
        
        Args:
            preferences: A dictionary containing the user's scheduling preferences. For example: {"preferred_time": "morning", "timezone": "UTC"}
        """
        logger.info(f"LLM Tool Call: schedule_program for {user_id}")
        if not scheduler:
            return "Failed: Scheduler is not configured."
        try:
            session = await memory_manager.get_active_session(user_id)
            if not session:
                return "Failed: No active session found."
            
            # Assuming schedule_daily_check_ins is synchronous or asynchronous
            # Looking at main.py earlier, it was called synchronously: self.scheduler.schedule_daily_check_ins(result["session"])
            scheduler.schedule_daily_check_ins(session)
            return "Successfully scheduled the 28-day program check-ins for the user."
        except Exception as e:
            logger.error(f"Error in schedule_program: {e}")
            return f"Tool execution failed: {str(e)}"

    return [
        fetch_coping_strategies,
        save_wellness_plan,
        get_todays_tasks,
        mark_task_completed,
        schedule_program
    ]
