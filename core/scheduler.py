"""
Scheduling system for daily check-ins and wellness tasks
"""
from datetime import datetime, timedelta, time as dt_time
from typing import Callable, Dict, Any, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from loguru import logger
import uuid

from config import CHECK_IN_TIMES
from models import UserSession, WellnessTask, TaskType, TaskStatus
from core.memory import MemoryManager


class WellnessScheduler:
    """Manages scheduling of check-ins and wellness tasks"""
    
    def __init__(self, memory_manager: MemoryManager):
        """Initialize scheduler"""
        self.scheduler = BackgroundScheduler()
        self.memory = memory_manager
        self.check_in_callbacks: Dict[str, Callable] = {}
        self.task_callbacks: Dict[str, Callable] = {}
        
        logger.info("Wellness Scheduler initialized")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")

    def stop(self):
        """Alias for shutdown to be compatible with main.py"""
        self.shutdown()
    
    def register_check_in_callback(self, name: str, callback: Callable):
        """Register a callback function for check-ins"""
        self.check_in_callbacks[name] = callback
        logger.info(f"Registered check-in callback: {name}")
    
    def register_task_callback(self, name: str, callback: Callable):
        """Register a callback function for tasks"""
        self.task_callbacks[name] = callback
        logger.info(f"Registered task callback: {name}")
    
    def schedule_daily_check_ins(
        self,
        session: UserSession,
        callback_name: str = "default"
    ) -> List[str]:
        """
        Schedule daily check-ins for a session
        
        Args:
            session: User session
            callback_name: Name of registered callback to use
            
        Returns:
            List of job IDs created
        """
        if callback_name not in self.check_in_callbacks:
            raise ValueError(f"No callback registered with name: {callback_name}")
        
        callback = self.check_in_callbacks[callback_name]
        job_ids = []
        
        # Parse check-in times
        check_in_time_names = ["morning", "midday", "afternoon", "evening"]
        
        for i, check_in_time_str in enumerate(CHECK_IN_TIMES):
            hour, minute = map(int, check_in_time_str.split(':'))
            time_name = check_in_time_names[i] if i < len(check_in_time_names) else f"checkin_{i+1}"
            
            # Schedule for each day of the program
            for day in range(session.duration_days):
                scheduled_date = session.start_date + timedelta(days=day)
                scheduled_datetime = datetime.combine(
                    scheduled_date.date(),
                    dt_time(hour, minute)
                )
                
                # Only schedule if in the future
                if scheduled_datetime > datetime.now():
                    job_id = f"checkin_{session.session_id}_{day}_{time_name}"
                    
                    self.scheduler.add_job(
                        callback,
                        trigger=DateTrigger(run_date=scheduled_datetime),
                        args=[session.session_id, time_name, day + 1],
                        id=job_id,
                        replace_existing=True
                    )
                    
                    job_ids.append(job_id)
                    logger.info(f"Scheduled check-in: {job_id} at {scheduled_datetime}")
        
        return job_ids
    
    def schedule_task(
        self,
        task: WellnessTask,
        callback_name: str = "default"
    ) -> str:
        """
        Schedule a wellness task
        
        Args:
            task: Wellness task to schedule
            callback_name: Name of registered callback to use
            
        Returns:
            Job ID
        """
        if callback_name not in self.task_callbacks:
            raise ValueError(f"No callback registered with name: {callback_name}")
        
        callback = self.task_callbacks[callback_name]
        
        # Only schedule if in the future
        if task.scheduled_time > datetime.now():
            job_id = f"task_{task.task_id}"
            
            self.scheduler.add_job(
                callback,
                trigger=DateTrigger(run_date=task.scheduled_time),
                args=[task.task_id, task.session_id],
                id=job_id,
                replace_existing=True
            )
            
            logger.info(f"Scheduled task: {job_id} at {task.scheduled_time}")
            return job_id
        
        return ""
    
    def schedule_program_tasks(
        self,
        session: UserSession,
        tasks: List[WellnessTask],
        callback_name: str = "default"
    ) -> List[str]:
        """
        Schedule all tasks for a wellness program
        
        Args:
            session: User session
            tasks: List of wellness tasks
            callback_name: Name of registered callback to use
            
        Returns:
            List of job IDs created
        """
        job_ids = []
        
        for task in tasks:
            job_id = self.schedule_task(task, callback_name)
            if job_id:
                job_ids.append(job_id)
        
        logger.info(f"Scheduled {len(job_ids)} tasks for session {session.session_id}")
        return job_ids
    
    def cancel_session_jobs(self, session_id: str):
        """Cancel all jobs for a session"""
        jobs = self.scheduler.get_jobs()
        cancelled_count = 0
        
        for job in jobs:
            if session_id in job.id:
                job.remove()
                cancelled_count += 1
        
        logger.info(f"Cancelled {cancelled_count} jobs for session {session_id}")
    
    def get_upcoming_tasks(
        self,
        session_id: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get upcoming tasks for a session within specified hours"""
        jobs = self.scheduler.get_jobs()
        upcoming = []
        
        cutoff_time = datetime.now() + timedelta(hours=hours)
        
        for job in jobs:
            if session_id in job.id and job.next_run_time:
                if job.next_run_time <= cutoff_time:
                    upcoming.append({
                        "job_id": job.id,
                        "next_run": job.next_run_time,
                        "job_type": "check_in" if "checkin_" in job.id else "task"
                    })
        
        # Sort by next run time
        upcoming.sort(key=lambda x: x["next_run"])
        return upcoming
    
    def create_wellness_tasks_from_plan(
        self,
        session: UserSession,
        wellness_plan: Dict[str, Any]
    ) -> List[WellnessTask]:
        """
        Create WellnessTask objects from a wellness plan
        
        Args:
            session: User session
            wellness_plan: Generated wellness plan
            
        Returns:
            List of WellnessTask objects
        """
        tasks = []
        
        # Extract calendar tasks from plan
        calendar_tasks = wellness_plan.get("CALENDAR TASKS", [])
        
        if isinstance(calendar_tasks, list):
            for i, task_info in enumerate(calendar_tasks):
                # Parse task info
                if isinstance(task_info, dict):
                    title = task_info.get("title", f"Wellness Activity {i+1}")
                    description = task_info.get("description", "")
                    time_str = task_info.get("time", "09:00")
                    day = task_info.get("day", 1)
                    duration = task_info.get("duration_minutes", 15)
                    task_type_str = task_info.get("type", "mindfulness")
                else:
                    # Fallback for string format
                    title = str(task_info)
                    description = title
                    time_str = "09:00"
                    day = (i % session.duration_days) + 1
                    duration = 15
                    task_type_str = "mindfulness"
                
                # Map task type
                task_type = self._map_task_type(task_type_str)
                
                # Calculate scheduled time
                hour, minute = map(int, time_str.split(':'))
                scheduled_date = session.start_date + timedelta(days=day - 1)
                scheduled_time = datetime.combine(
                    scheduled_date.date(),
                    dt_time(hour, minute)
                )
                
                # Create task
                task = WellnessTask(
                    task_id=str(uuid.uuid4()),
                    session_id=session.session_id,
                    user_id=session.user_id,
                    task_type=task_type,
                    title=title,
                    description=description,
                    instructions=description,
                    scheduled_time=scheduled_time,
                    duration_minutes=duration,
                    status=TaskStatus.PENDING
                )
                
                tasks.append(task)
        
        # If no calendar tasks, create default tasks
        if not tasks:
            tasks = self._create_default_tasks(session)
        
        logger.info(f"Created {len(tasks)} wellness tasks for session {session.session_id}")
        return tasks
    
    def _map_task_type(self, type_str: str) -> TaskType:
        """Map string to TaskType enum"""
        type_mapping = {
            "breathing": TaskType.BREATHING_EXERCISE,
            "exercise": TaskType.PHYSICAL_ACTIVITY,
            "physical": TaskType.PHYSICAL_ACTIVITY,
            "social": TaskType.SOCIAL_CONNECTION,
            "creative": TaskType.CREATIVE_EXPRESSION,
            "mindfulness": TaskType.MINDFULNESS,
            "meditation": TaskType.MINDFULNESS,
            "self_care": TaskType.SELF_CARE,
            "journal": TaskType.JOURNALING,
            "journaling": TaskType.JOURNALING,
            "relaxation": TaskType.RELAXATION,
            "goal": TaskType.GOAL_SETTING
        }
        
        return type_mapping.get(type_str.lower(), TaskType.MINDFULNESS)
    
    def _create_default_tasks(self, session: UserSession) -> List[WellnessTask]:
        """Create default wellness tasks"""
        default_tasks = [
            {
                "type": TaskType.BREATHING_EXERCISE,
                "title": "Morning Breathing Exercise",
                "description": "Practice 4-7-8 breathing for 5 minutes",
                "time": "08:00",
                "duration": 5
            },
            {
                "type": TaskType.PHYSICAL_ACTIVITY,
                "title": "Midday Walk",
                "description": "Take a 15-minute walk outside",
                "time": "12:30",
                "duration": 15
            },
            {
                "type": TaskType.JOURNALING,
                "title": "Evening Journaling",
                "description": "Write about your day and feelings",
                "time": "20:00",
                "duration": 10
            }
        ]
        
        tasks = []
        for day in range(min(session.duration_days, 7)):
            for task_template in default_tasks:
                hour, minute = map(int, task_template["time"].split(':'))
                scheduled_date = session.start_date + timedelta(days=day)
                scheduled_time = datetime.combine(
                    scheduled_date.date(),
                    dt_time(hour, minute)
                )
                
                task = WellnessTask(
                    task_id=str(uuid.uuid4()),
                    session_id=session.session_id,
                    user_id=session.user_id,
                    task_type=task_template["type"],
                    title=f"{task_template['title']} - Day {day + 1}",
                    description=task_template["description"],
                    instructions=task_template["description"],
                    scheduled_time=scheduled_time,
                    duration_minutes=task_template["duration"],
                    status=TaskStatus.PENDING
                )
                
                tasks.append(task)
        
        return tasks
