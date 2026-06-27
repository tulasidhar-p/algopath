import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models import Domain, Topic, Pattern, Concept, Question, UserProgress, UserTopicProgress
from app.schemas.user import APIResponse
from app.schemas.domain import DomainResponse, DomainRoadmapData
from app.schemas.curriculum import (
    TopicResponse,
    TopicProgressDetail,
    PatternResponse,
    ConceptResponse,
    QuestionResponse,
    SolveRequest,
    BookmarkRequest
)
from app.services import auth_service, roadmap_service

router = APIRouter(prefix="/api", tags=["Curriculum"])

# 1. GET /api/domains
@router.get("/domains", response_model=APIResponse[List[DomainResponse]])
def get_domains(db: Session = Depends(get_db)):
    domains = db.query(Domain).order_by(Domain.order_index).all()
    domain_data = [DomainResponse.from_orm(d) for d in domains]
    return {"success": True, "data": domain_data}

# 2. GET /api/domains/{slug}
@router.get("/domains/{slug}", response_model=APIResponse[DomainResponse])
def get_domain(slug: str, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.slug == slug).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {"success": True, "data": DomainResponse.from_orm(domain)}

# 3. GET /api/domains/{slug}/roadmap
@router.get("/domains/{slug}/roadmap", response_model=APIResponse[DomainRoadmapData])
def get_domain_roadmap(slug: str, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    roadmap = roadmap_service.get_domain_roadmap(db, slug, current_user.id)
    if not roadmap:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {"success": True, "data": roadmap}

# 4. GET /api/topics/{slug}
@router.get("/topics/{slug}", response_model=APIResponse[TopicResponse])
def get_topic(slug: str, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Fetch UserTopicProgress to determine if it is unlocked
    progress = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == current_user.id,
        UserTopicProgress.topic_id == topic.id
    ).first()
    
    is_unlocked = progress.is_unlocked if progress else (topic.order_index == 1 or not topic.prerequisites)

    # Collect all questions in this topic to query user progress in bulk
    question_ids = []
    for pattern in topic.patterns:
        for concept in pattern.concepts:
            for question in concept.questions:
                question_ids.append(question.id)

    user_progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id.in_(question_ids) if question_ids else False
    ).all()
    progress_by_q = {up.question_id: up for up in user_progress_list}

    topic_solved_count = 0
    patterns_response = []
    
    for pattern in sorted(topic.patterns, key=lambda x: x.order_index):
        pattern_solved = 0
        pattern_total = 0
        concepts_response = []
        
        for concept in sorted(pattern.concepts, key=lambda x: x.order_index):
            concept_solved = 0
            concept_total = 0
            questions_response = []
            
            for question in sorted(concept.questions, key=lambda x: x.order_index):
                q_progress = progress_by_q.get(question.id)
                status = q_progress.status if q_progress else "unsolved"
                bookmark = q_progress.bookmark if q_progress else False
                notes = q_progress.notes if q_progress else None

                if status == "solved":
                    concept_solved += 1
                    topic_solved_count += 1

                concept_total += 1
                
                tags = [t.name for t in question.tags]
                companies = [c.name for c in question.companies]

                questions_response.append(QuestionResponse(
                    id=question.id,
                    concept_id=question.concept_id,
                    title=question.title,
                    difficulty=question.difficulty,
                    source=question.source,
                    url=question.url,
                    estimated_solve_time=question.estimated_solve_time,
                    is_important=question.is_important,
                    order_index=question.order_index,
                    status=status,
                    bookmark=bookmark,
                    notes=notes,
                    tags=tags,
                    companies=companies
                ))

            concept_objectives = []
            if concept.learning_objectives:
                try:
                    concept_objectives = json.loads(concept.learning_objectives)
                except Exception:
                    concept_objectives = []

            concepts_response.append(ConceptResponse(
                id=concept.id,
                pattern_id=concept.pattern_id,
                name=concept.name,
                slug=concept.slug,
                theory_markdown=concept.theory_markdown,
                learning_objectives=concept_objectives,
                order_index=concept.order_index,
                questions=questions_response,
                solved_count=concept_solved,
                total_count=concept_total
            ))
            pattern_solved += concept_solved
            pattern_total += concept_total

        patterns_response.append(PatternResponse(
            id=pattern.id,
            topic_id=pattern.topic_id,
            name=pattern.name,
            slug=pattern.slug,
            description=pattern.description,
            order_index=pattern.order_index,
            concepts=concepts_response,
            solved_count=pattern_solved,
            total_count=pattern_total
        ))

    topic_objectives = []
    if topic.learning_objectives:
        try:
            topic_objectives = json.loads(topic.learning_objectives)
        except Exception:
            topic_objectives = []

    prereqs = [p.slug for p in topic.prerequisites]

    # Keep database Cache of solved count correct
    if progress:
        if progress.solved_count != topic_solved_count:
            progress.solved_count = topic_solved_count
            db.add(progress)
            db.commit()
            db.refresh(progress)

    data = TopicResponse(
        id=topic.id,
        domain_id=topic.domain_id,
        name=topic.name,
        slug=topic.slug,
        description=topic.description,
        order_index=topic.order_index,
        icon=topic.icon,
        unlock_percentage=topic.unlock_percentage,
        learning_objectives=topic_objectives,
        total_questions=topic.total_questions,
        solved_count=topic_solved_count,
        is_unlocked=is_unlocked,
        patterns=patterns_response,
        prerequisites=prereqs
    )
    return {"success": True, "data": data}

# 5. GET /api/topics/{slug}/progress
@router.get("/topics/{slug}/progress", response_model=APIResponse[TopicProgressDetail])
def get_topic_progress(slug: str, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    topic = db.query(Topic).filter(Topic.slug == slug).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    progress = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == current_user.id,
        UserTopicProgress.topic_id == topic.id
    ).first()

    solved = progress.solved_count if progress else 0
    total = progress.total_count if progress else topic.total_questions
    is_unlocked = progress.is_unlocked if progress else (topic.order_index == 1 or not topic.prerequisites)
    pct = (solved / total) if total > 0 else 0.0

    data = TopicProgressDetail(
        topic_slug=topic.slug,
        solved_count=solved,
        total_count=total,
        is_unlocked=is_unlocked,
        completion_percentage=pct
    )
    return {"success": True, "data": data}

# 6. GET /api/patterns/{slug}
@router.get("/patterns/{slug}", response_model=APIResponse[PatternResponse])
def get_pattern(slug: str, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    pattern = db.query(Pattern).filter(Pattern.slug == slug).first()
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")

    # Fetch nested concepts and questions with user progress
    question_ids = []
    for concept in pattern.concepts:
        for question in concept.questions:
            question_ids.append(question.id)

    user_progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id.in_(question_ids) if question_ids else False
    ).all()
    progress_by_q = {up.question_id: up for up in user_progress_list}

    pattern_solved = 0
    pattern_total = 0
    concepts_response = []

    for concept in sorted(pattern.concepts, key=lambda x: x.order_index):
        concept_solved = 0
        concept_total = 0
        questions_response = []

        for question in sorted(concept.questions, key=lambda x: x.order_index):
            q_progress = progress_by_q.get(question.id)
            status = q_progress.status if q_progress else "unsolved"
            bookmark = q_progress.bookmark if q_progress else False
            notes = q_progress.notes if q_progress else None

            if status == "solved":
                concept_solved += 1

            concept_total += 1
            
            tags = [t.name for t in question.tags]
            companies = [c.name for c in question.companies]

            questions_response.append(QuestionResponse(
                id=question.id,
                concept_id=question.concept_id,
                title=question.title,
                difficulty=question.difficulty,
                source=question.source,
                url=question.url,
                estimated_solve_time=question.estimated_solve_time,
                is_important=question.is_important,
                order_index=question.order_index,
                status=status,
                bookmark=bookmark,
                notes=notes,
                tags=tags,
                companies=companies
            ))

        concept_objectives = []
        if concept.learning_objectives:
            try:
                concept_objectives = json.loads(concept.learning_objectives)
            except Exception:
                concept_objectives = []

        concepts_response.append(ConceptResponse(
            id=concept.id,
            pattern_id=concept.pattern_id,
            name=concept.name,
            slug=concept.slug,
            theory_markdown=concept.theory_markdown,
            learning_objectives=concept_objectives,
            order_index=concept.order_index,
            questions=questions_response,
            solved_count=concept_solved,
            total_count=concept_total
        ))
        pattern_solved += concept_solved
        pattern_total += concept_total

    data = PatternResponse(
        id=pattern.id,
        topic_id=pattern.topic_id,
        name=pattern.name,
        slug=pattern.slug,
        description=pattern.description,
        order_index=pattern.order_index,
        concepts=concepts_response,
        solved_count=pattern_solved,
        total_count=pattern_total
    )
    return {"success": True, "data": data}

# 7. GET /api/concepts/{slug}
@router.get("/concepts/{slug}", response_model=APIResponse[ConceptResponse])
def get_concept(slug: str, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    concept = db.query(Concept).filter(Concept.slug == slug).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    question_ids = [q.id for q in concept.questions]
    user_progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id.in_(question_ids) if question_ids else False
    ).all()
    progress_by_q = {up.question_id: up for up in user_progress_list}

    concept_solved = 0
    concept_total = 0
    questions_response = []

    for question in sorted(concept.questions, key=lambda x: x.order_index):
        q_progress = progress_by_q.get(question.id)
        status = q_progress.status if q_progress else "unsolved"
        bookmark = q_progress.bookmark if q_progress else False
        notes = q_progress.notes if q_progress else None

        if status == "solved":
            concept_solved += 1

        concept_total += 1
        
        tags = [t.name for t in question.tags]
        companies = [c.name for c in question.companies]

        questions_response.append(QuestionResponse(
            id=question.id,
            concept_id=question.concept_id,
            title=question.title,
            difficulty=question.difficulty,
            source=question.source,
            url=question.url,
            estimated_solve_time=question.estimated_solve_time,
            is_important=question.is_important,
            order_index=question.order_index,
            status=status,
            bookmark=bookmark,
            notes=notes,
            tags=tags,
            companies=companies
        ))

    concept_objectives = []
    if concept.learning_objectives:
        try:
            concept_objectives = json.loads(concept.learning_objectives)
        except Exception:
            concept_objectives = []

    data = ConceptResponse(
        id=concept.id,
        pattern_id=concept.pattern_id,
        name=concept.name,
        slug=concept.slug,
        theory_markdown=concept.theory_markdown,
        learning_objectives=concept_objectives,
        order_index=concept.order_index,
        questions=questions_response,
        solved_count=concept_solved,
        total_count=concept_total
    )
    return {"success": True, "data": data}

# 8. GET /api/questions
@router.get("/questions", response_model=APIResponse[List[QuestionResponse]])
def get_questions(db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    questions = db.query(Question).all()
    question_ids = [q.id for q in questions]

    user_progress_list = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id.in_(question_ids) if question_ids else False
    ).all()
    progress_by_q = {up.question_id: up for up in user_progress_list}

    data = []
    for question in sorted(questions, key=lambda x: x.id):
        q_progress = progress_by_q.get(question.id)
        status = q_progress.status if q_progress else "unsolved"
        bookmark = q_progress.bookmark if q_progress else False
        notes = q_progress.notes if q_progress else None

        tags = [t.name for t in question.tags]
        companies = [c.name for c in question.companies]

        data.append(QuestionResponse(
            id=question.id,
            concept_id=question.concept_id,
            title=question.title,
            difficulty=question.difficulty,
            source=question.source,
            url=question.url,
            estimated_solve_time=question.estimated_solve_time,
            is_important=question.is_important,
            order_index=question.order_index,
            status=status,
            bookmark=bookmark,
            notes=notes,
            tags=tags,
            companies=companies
        ))

    return {"success": True, "data": data}

# 9. GET /api/questions/{id}
@router.get("/questions/{id}", response_model=APIResponse[QuestionResponse])
def get_question(id: int, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    q_progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id == id
    ).first()

    status = q_progress.status if q_progress else "unsolved"
    bookmark = q_progress.bookmark if q_progress else False
    notes = q_progress.notes if q_progress else None

    tags = [t.name for t in question.tags]
    companies = [c.name for c in question.companies]

    data = QuestionResponse(
        id=question.id,
        concept_id=question.concept_id,
        title=question.title,
        difficulty=question.difficulty,
        source=question.source,
        url=question.url,
        estimated_solve_time=question.estimated_solve_time,
        is_important=question.is_important,
        order_index=question.order_index,
        status=status,
        bookmark=bookmark,
        notes=notes,
        tags=tags,
        companies=companies
    )
    return {"success": True, "data": data}

# 10. PATCH /api/questions/{id}/solve
@router.patch("/questions/{id}/solve")
def solve_question(id: int, req: SolveRequest, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # 1. Update or create UserProgress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id == id
    ).first()

    was_solved = False
    if progress:
        was_solved = (progress.status == "solved")
        progress.status = req.status
        if req.notes is not None:
            progress.notes = req.notes
        if req.solve_time is not None:
            progress.solve_time = req.solve_time
        
        if req.status == "solved" and not was_solved:
            progress.solved_at = datetime.utcnow()
        elif req.status != "solved":
            progress.solved_at = None
        db.add(progress)
    else:
        progress = UserProgress(
            user_id=current_user.id,
            question_id=id,
            status=req.status,
            notes=req.notes,
            solve_time=req.solve_time or 0,
            solved_at=datetime.utcnow() if req.status == "solved" else None
        )
        db.add(progress)
    db.flush()

    # 2. Update the corresponding UserTopicProgress solved count
    topic_id = question.concept.pattern.topic_id
    
    # Query all questions under this topic
    topic_questions = db.query(Question).join(Concept).join(Pattern).filter(Pattern.topic_id == topic_id).all()
    topic_question_ids = [q.id for q in topic_questions]

    solved_count = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id.in_(topic_question_ids),
        UserProgress.status == "solved"
    ).count()

    topic_progress = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == current_user.id,
        UserTopicProgress.topic_id == topic_id
    ).first()

    if not topic_progress:
        topic_progress = UserTopicProgress(
            user_id=current_user.id,
            topic_id=topic_id,
            solved_count=solved_count,
            total_count=len(topic_question_ids),
            is_unlocked=(question.concept.pattern.topic.order_index == 1)
        )
        db.add(topic_progress)
    else:
        topic_progress.solved_count = solved_count
        topic_progress.total_count = len(topic_question_ids)
        db.add(topic_progress)
    db.flush()

    # 3. Recalculate unlock status of all topics in this domain
    domain_id = question.concept.pattern.topic.domain_id
    all_topics = db.query(Topic).filter(Topic.domain_id == domain_id).order_by(Topic.order_index).all()
    
    user_topic_progresses = db.query(UserTopicProgress).filter(
        UserTopicProgress.user_id == current_user.id
    ).all()
    progress_map = {up.topic_id: up for up in user_topic_progresses}

    for t in all_topics:
        t_progress = progress_map.get(t.id)
        if not t_progress:
            # Create a default locked/unlocked progress record
            is_unlocked_default = (t.order_index == 1 or not t.prerequisites)
            t_progress = UserTopicProgress(
                user_id=current_user.id,
                topic_id=t.id,
                solved_count=0,
                total_count=t.total_questions,
                is_unlocked=is_unlocked_default
            )
            db.add(t_progress)
            db.flush()
            progress_map[t.id] = t_progress

        if t.order_index == 1 or not t.prerequisites:
            t_progress.is_unlocked = True
        else:
            prereqs_met = True
            for prereq in t.prerequisites:
                prereq_progress = progress_map.get(prereq.id)
                prereq_solved = prereq_progress.solved_count if prereq_progress else 0
                prereq_total = prereq_progress.total_count if prereq_progress else prereq.total_questions
                
                prereq_pct = (prereq_solved / prereq_total) if prereq_total > 0 else 0.0
                is_prereq_unlocked = prereq_progress.is_unlocked if prereq_progress else False
                
                if not is_prereq_unlocked or prereq_pct < prereq.unlock_percentage:
                    prereqs_met = False
                    break
            t_progress.is_unlocked = prereqs_met
        db.add(t_progress)

    db.commit()

    return {
        "success": True,
        "data": {
            "question_id": id,
            "status": progress.status,
            "notes": progress.notes,
            "solve_time": progress.solve_time,
            "topic_solved_count": topic_progress.solved_count,
            "topic_total_count": topic_progress.total_count,
            "topic_is_unlocked": topic_progress.is_unlocked
        }
    }

# 11. PATCH /api/questions/{id}/bookmark
@router.patch("/questions/{id}/bookmark")
def bookmark_question(id: int, req: BookmarkRequest, db: Session = Depends(get_db), current_user = Depends(auth_service.get_current_user)):
    question = db.query(Question).filter(Question.id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.question_id == id
    ).first()

    if progress:
        progress.bookmark = req.bookmark
        db.add(progress)
    else:
        progress = UserProgress(
            user_id=current_user.id,
            question_id=id,
            bookmark=req.bookmark,
            status="unsolved"
        )
        db.add(progress)
    db.commit()

    return {
        "success": True,
        "data": {
            "question_id": id,
            "bookmark": progress.bookmark
        }
    }
