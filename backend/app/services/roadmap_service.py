import json
from sqlalchemy.orm import Session
from app.repositories import domain_repo
from app.models import Topic, UserTopicProgress

def get_domain_roadmap(db: Session, domain_slug: str, user_id: int):
    domain = domain_repo.get_domain_by_slug(db, domain_slug)
    if not domain:
        return None

    topics = domain_repo.get_topics_by_domain_id(db, domain.id)
    progress_map = domain_repo.get_all_user_topic_progresses(db, user_id)

    # Dictionary to keep track of calculated unlock status and solved percentages
    solved_percentages = {}
    roadmap_data = []

    for topic in topics:
        progress = progress_map.get(topic.id)
        solved_count = progress.solved_count if progress else 0
        total_count = progress.total_count if progress else topic.total_questions

        # Calculate completion fraction
        pct = (solved_count / total_count) if total_count > 0 else 0.0
        solved_percentages[topic.id] = pct

        # Determine unlock status
        is_unlocked = False
        if topic.order_index == 1 or not topic.prerequisites:
            is_unlocked = True
        else:
            # All prerequisites must meet their required unlock percentages
            prereqs_met = True
            for prereq in topic.prerequisites:
                prereq_progress = progress_map.get(prereq.id)
                prereq_solved = prereq_progress.solved_count if prereq_progress else 0
                prereq_total = prereq_progress.total_count if prereq_progress else prereq.total_questions
                
                prereq_pct = (prereq_solved / prereq_total) if prereq_total > 0 else 0.0
                if prereq_pct < prereq.unlock_percentage:
                    prereqs_met = False
                    break
            
            is_unlocked = prereqs_met

        # Keep cache updated if it exists
        if progress and progress.is_unlocked != is_unlocked:
            progress.is_unlocked = is_unlocked
            db.add(progress)

        # Parse learning objectives
        learning_objs = []
        if topic.learning_objectives:
            try:
                learning_objs = json.loads(topic.learning_objectives)
            except Exception:
                learning_objs = []

        # Parse prerequisite slugs/names
        prereq_slugs = [p.slug for p in topic.prerequisites]

        roadmap_data.append({
            "id": topic.id,
            "name": topic.name,
            "slug": topic.slug,
            "description": topic.description,
            "order_index": topic.order_index,
            "icon": topic.icon,
            "unlock_percentage": topic.unlock_percentage,
            "learning_objectives": learning_objs,
            "total_questions": total_count,
            "solved_count": solved_count,
            "is_unlocked": is_unlocked,
            "prerequisites": prereq_slugs
        })

    db.commit()
    return {
        "domain": {
            "name": domain.name,
            "slug": domain.slug,
            "description": domain.description
        },
        "topics": roadmap_data
    }
