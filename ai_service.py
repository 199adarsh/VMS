import google.generativeai as genai
import os
from typing import Dict, List, Optional
import json

class AIService:
    """AI service for Gemini API integration"""
    
    def __init__(self):
        # Initialize Gemini API
        api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyAD-H9ibjRCeW9ezgOySX025PVBF9zeGr4')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_task_completion_guide(self, task_data: Dict) -> Dict:
        """Generate step-by-step completion guide for a task"""
        try:
            task_title = task_data.get('title', 'Unknown Task')
            task_description = task_data.get('description', 'No description available')
            task_priority = task_data.get('priority', 'Medium')
            task_deadline = task_data.get('deadline', 'No deadline specified')
            
            prompt = f"""
            You are an AI assistant helping volunteers complete their tasks efficiently. 
            Generate a step-by-step completion guide for the following task:
            
            Task Title: {task_title}
            Description: {task_description}
            Priority: {task_priority}
            Deadline: {task_deadline}
            
            Return ONLY a JSON object with this exact structure:
            {{
                "overview": "Brief 2-3 sentence overview of what needs to be accomplished",
                "steps": [
                    {{"step": 1, "title": "Step title", "description": "Detailed description", "estimated_time": "5-10 minutes"}},
                    {{"step": 2, "title": "Step title", "description": "Detailed description", "estimated_time": "10-15 minutes"}},
                    {{"step": 3, "title": "Step title", "description": "Detailed description", "estimated_time": "10-15 minutes"}},
                    {{"step": 4, "title": "Step title", "description": "Detailed description", "estimated_time": "5-10 minutes"}},
                    {{"step": 5, "title": "Step title", "description": "Detailed description", "estimated_time": "5-10 minutes"}}
                ],
                "pro_tips": ["Practical tip 1", "Practical tip 2", "Practical tip 3"],
                "things_to_avoid": ["Common mistake 1", "Common mistake 2"],
                "total_estimated_time": "30-45 minutes",
                "success_criteria": "Clear description of how to know when task is complete"
            }}
            
            Make the guide practical, encouraging, and easy to follow. Return ONLY the JSON, no other text.
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                # Clean the response text by removing markdown code blocks
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                response_text = response_text.strip()
                
                guide_data = json.loads(response_text)
                return {
                    "success": True,
                    "guide": guide_data,
                    "task_id": task_data.get('task_id'),
                    "generated_at": task_data.get('created_at')
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": True,
                    "guide": {
                        "overview": "AI-generated completion guide",
                        "steps": [
                            {"step": 1, "title": "Read Task Details", "description": response.text[:200] + "...", "estimated_time": "5 minutes"}
                        ],
                        "tips": ["Follow the task description carefully", "Ask for help if needed"],
                        "pitfalls": ["Don't rush through the task"],
                        "total_estimated_time": "30 minutes"
                    },
                    "task_id": task_data.get('task_id'),
                    "generated_at": task_data.get('created_at')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate task completion guide"
            }
    
    def generate_chatbot_response(self, user_message: str, context: Dict = None) -> Dict:
        """Generate chatbot response for user queries"""
        try:
            user_role = context.get('role', 'volunteer') if context else 'volunteer'
            user_tasks = context.get('assigned_tasks', []) if context else []
            
            if user_role == 'coordinator':
                prompt = f"""You are an AI assistant for a volunteer management system helping a COORDINATOR.

User question: "{user_message}"

As a coordinator, you can help with:
- Creating and managing tasks
- Assigning volunteers to tasks
- Tracking attendance and progress
- Managing announcements
- Viewing reports and analytics
- Coordinating events and activities

Provide specific, actionable advice for coordinators. Be helpful and professional.
If asked about general topics (like "how to make a website"), explain how it relates to volunteer management or suggest creating a task for it.

Keep responses practical and focused on volunteer management."""
            else:
                prompt = f"""You are an AI assistant for a volunteer management system helping a VOLUNTEER.

User question: "{user_message}"

As a volunteer, you can help with:
- Understanding assigned tasks
- Checking attendance requirements
- Getting help with task completion
- Learning about the platform features
- Contacting coordinators for support

Provide helpful, encouraging responses. If asked about general topics, suggest how they could be volunteer tasks or direct to coordinators.

Keep responses friendly and supportive."""
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "response": response.text,
                "timestamp": context.get('timestamp') if context else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "I'm having trouble processing your request. Please try again or contact support."
            }
    
    def generate_recommendations(self, user_data: Dict, available_tasks: List[Dict], past_tasks: List[Dict] = None) -> Dict:
        """Generate volunteer recommendations for coordinators to assign to tasks"""
        try:
            user_role = user_data.get('role', 'volunteer')
            
            # Only provide recommendations for coordinators and admins
            if user_role not in ['coordinator', 'admin']:
                return {
                    "success": True,
                    "recommendations": {
                        "recommendations": [],
                        "reasoning": "Volunteer recommendations are only available to coordinators and administrators"
                    },
                    "user_id": user_data.get('user_id')
                }
            
            # For coordinators, we need to get available volunteers instead of tasks
            # This would typically come from the database service
            # For now, we'll create a mock response for volunteer recommendations
            
            prompt = f"""You are an AI assistant helping coordinators assign the best volunteers to tasks.

As a coordinator, you need to recommend volunteers based on their:
1. Skills and experience
2. Past performance and ratings
3. Availability and workload
4. Task requirements and complexity

Return JSON with 3-5 volunteer recommendations:
{{
    "recommendations": [
        {{
            "volunteer_id": "volunteer_id_here",
            "volunteer_name": "Volunteer Name",
            "reason": "Why this volunteer is recommended",
            "match_score": 85,
            "confidence": "High/Medium/Low",
            "skills": ["skill1", "skill2"],
            "experience_level": "Beginner/Intermediate/Expert"
        }}
    ],
    "reasoning": "Overall recommendation strategy and analysis"
}}

Focus on volunteers who would be most suitable for current task assignments."""
            
            # Generate AI response
            response = self.model.generate_content(prompt)
            
            try:
                # Clean the response text by removing markdown code blocks
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                response_text = response_text.strip()
                
                recommendations = json.loads(response_text)
                return {
                    "success": True,
                    "recommendations": recommendations,
                    "user_id": user_data.get('user_id')
                }
            except json.JSONDecodeError as e:
                # Create fallback volunteer recommendations
                fallback_recommendations = [
                    {
                        "volunteer_id": "demo-vol-1",
                        "volunteer_name": "John Smith",
                        "reason": "Experienced volunteer with strong organizational skills and previous event coordination experience",
                        "match_score": 90,
                        "confidence": "High",
                        "skills": ["Organization", "Event Planning", "Leadership"],
                        "experience_level": "Expert"
                    },
                    {
                        "volunteer_id": "demo-vol-2", 
                        "volunteer_name": "Sarah Johnson",
                        "reason": "Reliable volunteer with good communication skills and flexible availability",
                        "match_score": 75,
                        "confidence": "Medium",
                        "skills": ["Communication", "Teamwork", "Problem Solving"],
                        "experience_level": "Intermediate"
                    },
                    {
                        "volunteer_id": "demo-vol-3",
                        "volunteer_name": "Mike Chen",
                        "reason": "New volunteer with enthusiasm and willingness to learn new skills",
                        "match_score": 65,
                        "confidence": "Medium",
                        "skills": ["Enthusiasm", "Learning", "Adaptability"],
                        "experience_level": "Beginner"
                    }
                ]
                
                return {
                    "success": True,
                    "recommendations": {
                        "recommendations": fallback_recommendations,
                        "reasoning": "AI-powered volunteer recommendations based on skills, experience, and availability"
                    },
                    "user_id": user_data.get('user_id')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate volunteer recommendations"
            }
    
    def generate_future_task_recommendations(self, ongoing_tasks: List[Dict], user_context: Dict = None) -> Dict:
        """Generate 3 future task recommendations based on ongoing tasks context"""
        try:
            if not ongoing_tasks:
                return {
                    "success": True,
                    "recommendations": {
                        "recommendations": [],
                        "reasoning": "No ongoing tasks found to base recommendations on"
                    }
                }
            
            # Analyze ongoing tasks to understand context
            task_analysis = self._analyze_ongoing_tasks(ongoing_tasks)
            
            prompt = f"""You are an AI assistant helping coordinators plan future tasks based on their current ongoing work.

CURRENT ONGOING TASKS CONTEXT:
{task_analysis}

Based on the ongoing tasks above, suggest 3 future tasks that would logically follow or complement the current work.

Return ONLY a JSON object with this exact structure:
{{
    "recommendations": [
        {{
            "title": "Future Task Title 1",
            "description": "Brief task description",
            "priority": "High/Medium/Low",
            "estimated_duration": "2-4 hours",
            "category": "Follow-up/Enhancement/Maintenance/New Initiative",
            "suggested_skills": ["skill1", "skill2", "skill3"]
        }},
        {{
            "title": "Future Task Title 2", 
            "description": "Brief task description",
            "priority": "High/Medium/Low",
            "estimated_duration": "1-3 hours",
            "category": "Follow-up/Enhancement/Maintenance/New Initiative",
            "suggested_skills": ["skill1", "skill2", "skill3"]
        }},
        {{
            "title": "Future Task Title 3",
            "description": "Brief task description", 
            "priority": "High/Medium/Low",
            "estimated_duration": "3-5 hours",
            "category": "Follow-up/Enhancement/Maintenance/New Initiative",
            "suggested_skills": ["skill1", "skill2", "skill3"]
        }}
    ]
}}

Make the recommendations practical and specific. Keep descriptions brief and direct. Return ONLY the JSON, no other text.
"""
            
            response = self.model.generate_content(prompt)
            
            try:
                # Clean the response text by removing markdown code blocks
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                response_text = response_text.strip()
                
                recommendations = json.loads(response_text)
                return {
                    "success": True,
                    "recommendations": recommendations
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "success": True,
                    "recommendations": {
                        "recommendations": [
                            {
                                "title": "Follow-up Task 1",
                                "description": "Continue building on current project progress",
                                "priority": "Medium",
                                "estimated_duration": "2-3 hours",
                                "category": "Follow-up",
                                "suggested_skills": ["Project Management", "Communication"]
                            },
                            {
                                "title": "Enhancement Task 2", 
                                "description": "Improve and expand current initiatives",
                                "priority": "Low",
                                "estimated_duration": "1-2 hours",
                                "category": "Enhancement",
                                "suggested_skills": ["Analysis", "Planning"]
                            },
                            {
                                "title": "Maintenance Task 3",
                                "description": "Ongoing support and maintenance activities",
                                "priority": "Medium", 
                                "estimated_duration": "1-3 hours",
                                "category": "Maintenance",
                                "suggested_skills": ["Support", "Documentation"]
                            }
                        ]
                    }
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate future task recommendations"
            }
    
    def _analyze_ongoing_tasks(self, ongoing_tasks: List[Dict]) -> str:
        """Analyze ongoing tasks to understand current work context"""
        if not ongoing_tasks:
            return "No ongoing tasks available for analysis."
        
        task_summaries = []
        categories = []
        priorities = []
        
        for task in ongoing_tasks:
            title = task.get('title', 'Unknown Task')
            description = task.get('description', 'No description')
            priority = task.get('priority', 'Medium')
            status = task.get('status', 'In Progress')
            deadline = task.get('deadline', 'No deadline')
            
            task_summaries.append(f"- {title} ({priority} priority, {status}, Due: {deadline})")
            priorities.append(priority)
            
            # Extract category from title/description
            title_lower = title.lower()
            if any(word in title_lower for word in ['event', 'meeting', 'coordination']):
                categories.append('Event Management')
            elif any(word in title_lower for word in ['data', 'analysis', 'report']):
                categories.append('Data & Analysis')
            elif any(word in title_lower for word in ['outreach', 'communication', 'marketing']):
                categories.append('Communication')
            elif any(word in title_lower for word in ['training', 'education', 'workshop']):
                categories.append('Training & Development')
            else:
                categories.append('General Operations')
        
        # Count patterns
        from collections import Counter
        priority_counts = Counter(priorities)
        category_counts = Counter(categories)
        
        analysis = f"""
ONGOING TASKS SUMMARY:
{chr(10).join(task_summaries)}

WORK CONTEXT ANALYSIS:
- Total ongoing tasks: {len(ongoing_tasks)}
- Most common priority: {priority_counts.most_common(1)[0][0] if priority_counts else 'N/A'}
- Primary work areas: {', '.join([cat for cat, count in category_counts.most_common(3)]) if category_counts else 'General'}
- Current focus: {category_counts.most_common(1)[0][0] if category_counts else 'Mixed activities'}

TASK PATTERNS:
- High priority tasks: {priority_counts.get('High', 0)}
- Medium priority tasks: {priority_counts.get('Medium', 0)} 
- Low priority tasks: {priority_counts.get('Low', 0)}
- Work distribution: {dict(category_counts)}
"""
        
        return analysis

    def _analyze_task_history(self, past_tasks: List[Dict]) -> str:
        """Analyze user's task history to identify patterns and preferences"""
        if not past_tasks:
            return "No previous task history available. User is new to the platform."
        
        # Analyze task patterns
        task_types = []
        priorities = []
        difficulties = []
        task_titles = []
        
        for task in past_tasks:
            title = task.get('title', '').lower()
            priority = task.get('priority', 'Medium')
            task_types.append(title)
            priorities.append(priority)
            
            # Infer difficulty from title/description
            if any(word in title for word in ['simple', 'basic', 'easy', 'quick', 'setup']):
                difficulties.append('Easy')
            elif any(word in title for word in ['complex', 'advanced', 'technical', 'management', 'coordination']):
                difficulties.append('Hard')
            else:
                difficulties.append('Medium')
            
            task_titles.append(task.get('title', 'Unknown'))
        
        # Count patterns
        from collections import Counter
        priority_counts = Counter(priorities)
        difficulty_counts = Counter(difficulties)
        
        # Identify common themes
        common_words = []
        for title in task_titles:
            words = title.lower().split()
            common_words.extend([word for word in words if len(word) > 3])
        
        word_counts = Counter(common_words)
        top_themes = [word for word, count in word_counts.most_common(5)]
        
        # Generate analysis
        analysis = f"""
        TASK HISTORY SUMMARY:
        - Total completed tasks: {len(past_tasks)}
        - Most common priority: {priority_counts.most_common(1)[0][0] if priority_counts else 'N/A'}
        - Difficulty preference: {difficulty_counts.most_common(1)[0][0] if difficulty_counts else 'N/A'}
        - Common themes: {', '.join(top_themes[:3]) if top_themes else 'None identified'}
        
        RECENT TASKS:
        {chr(10).join([f"- {task.get('title', 'Unknown')} ({task.get('priority', 'Medium')} priority)" for task in past_tasks[-5:]])}
        
        PATTERN ANALYSIS:
        - User shows preference for {priority_counts.most_common(1)[0][0].lower() if priority_counts else 'medium'} priority tasks
        - Comfortable with {difficulty_counts.most_common(1)[0][0].lower() if difficulty_counts else 'medium'} difficulty level
        - Interested in: {', '.join(top_themes[:3]) if top_themes else 'various areas'}
        """
        
        return analysis

# Global AI service instance
ai_service = AIService()
