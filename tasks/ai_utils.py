import spacy
from datetime import datetime, timedelta

nlp = spacy.load('en_core_web_sm')

def prioritize_task(task):
    due_date = task.due_date
    description = task.description.lower()
    doc = nlp(description)
    urgency_score = 0
    if due_date < datetime.now() + timedelta(days=2):
        urgency_score += 2
    for token in doc:
        if token.text in ['urgent', 'important', 'critical']:
            urgency_score += 1
    if urgency_score >= 3:
        return 'HIGH'
    elif urgency_score >= 1:
        return 'MEDIUM'
    return 'LOW'

def suggest_related_tasks(description):
    doc = nlp(description.lower())
    suggestions = []
    if any(token.text in ['meeting', 'call', 'discuss'] for token in doc):
        suggestions.append('Schedule meeting room')
    if any(token.text in ['presentation', 'slides', 'prepare'] for token in doc):
        suggestions.append('Practice presentation')
    return suggestions