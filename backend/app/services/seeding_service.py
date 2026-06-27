import os
import json
from sqlalchemy.orm import Session
from app.models import Domain, Topic, Pattern, Concept, Question, Tag, Company, User
from app.services.auth_service import get_password_hash

def seed_database(db: Session, seed_dir_path: str = None):
    if seed_dir_path is None:
        # Default path relative to this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        seed_dir_path = os.path.join(current_dir, "..", "..", "seed")
        seed_dir_path = os.path.abspath(seed_dir_path)

    if not os.path.exists(seed_dir_path):
        print(f"Seed directory not found at: {seed_dir_path}")
        return

    # Track prerequisites mapping: { topic_slug: [prereq_slugs] }
    prerequisites_map = {}

    # Scan directories under seed/
    domain_dirs = [
        os.path.join(seed_dir_path, d)
        for d in os.listdir(seed_dir_path)
        if os.path.isdir(os.path.join(seed_dir_path, d))
    ]

    for dom_dir in domain_dirs:
        domain_json_path = os.path.join(dom_dir, "domain.json")
        if not os.path.exists(domain_json_path):
            print(f"domain.json not found in {dom_dir}, skipping.")
            continue

        with open(domain_json_path, "r", encoding="utf-8") as f:
            dom_meta = json.load(f)

        # 1. Seed or update Domain
        domain = db.query(Domain).filter(Domain.slug == dom_meta["slug"]).first()
        if not domain:
            domain = Domain(
                name=dom_meta["name"],
                slug=dom_meta["slug"],
                description=dom_meta.get("description"),
                order_index=dom_meta["order_index"]
            )
            db.add(domain)
            db.flush()
        else:
            domain.name = dom_meta["name"]
            domain.description = dom_meta.get("description")
            domain.order_index = dom_meta["order_index"]
            db.add(domain)
            db.flush()

        # 2. Find and seed Topic files (all JSONs except domain.json)
        topic_files = [
            os.path.join(dom_dir, f)
            for f in os.listdir(dom_dir)
            if f.endswith(".json") and f != "domain.json"
        ]

        for topic_file in topic_files:
            with open(topic_file, "r", encoding="utf-8") as f:
                top_data = json.load(f)

            # Check or create Topic
            topic = db.query(Topic).filter(Topic.slug == top_data["slug"]).first()
            if not topic:
                topic = Topic(
                    domain_id=domain.id,
                    name=top_data["name"],
                    slug=top_data["slug"],
                    description=top_data.get("description"),
                    order_index=top_data["order_index"],
                    icon=top_data.get("icon"),
                    unlock_percentage=top_data.get("unlock_percentage", 0.3),
                    learning_objectives=json.dumps(top_data.get("learning_objectives", [])),
                    total_questions=0
                )
                db.add(topic)
                db.flush()
            else:
                topic.domain_id = domain.id
                topic.name = top_data["name"]
                topic.description = top_data.get("description")
                topic.order_index = top_data["order_index"]
                topic.icon = top_data.get("icon")
                topic.unlock_percentage = top_data.get("unlock_percentage", 0.3)
                topic.learning_objectives = json.dumps(top_data.get("learning_objectives", []))
                topic.total_questions = 0
                db.add(topic)
                db.flush()

            # Record prerequisites for this topic
            prerequisites_map[topic.slug] = top_data.get("prerequisites", [])

            # Seed Patterns
            patterns_data = top_data.get("patterns", [])
            for pat_data in patterns_data:
                pattern = db.query(Pattern).filter(Pattern.slug == pat_data["slug"]).first()
                if not pattern:
                    pattern = Pattern(
                        topic_id=topic.id,
                        name=pat_data["name"],
                        slug=pat_data["slug"],
                        description=pat_data.get("description"),
                        order_index=pat_data["order_index"]
                    )
                    db.add(pattern)
                    db.flush()
                else:
                    pattern.topic_id = topic.id
                    pattern.name = pat_data["name"]
                    pattern.description = pat_data.get("description")
                    pattern.order_index = pat_data["order_index"]
                    db.add(pattern)
                    db.flush()

                # Seed Concepts
                concepts_data = pat_data.get("concepts", [])
                for con_data in concepts_data:
                    concept = db.query(Concept).filter(Concept.slug == con_data["slug"]).first()
                    if not concept:
                        concept = Concept(
                            pattern_id=pattern.id,
                            name=con_data["name"],
                            slug=con_data["slug"],
                            theory_markdown=con_data.get("theory_markdown"),
                            learning_objectives=json.dumps(con_data.get("learning_objectives", [])),
                            order_index=con_data["order_index"]
                        )
                        db.add(concept)
                        db.flush()
                    else:
                        concept.pattern_id = pattern.id
                        concept.name = con_data["name"]
                        concept.theory_markdown = con_data.get("theory_markdown")
                        concept.learning_objectives = json.dumps(con_data.get("learning_objectives", []))
                        concept.order_index = con_data["order_index"]
                        db.add(concept)
                        db.flush()

                    # Seed Questions
                    questions_data = con_data.get("questions", [])
                    for q_data in questions_data:
                        question = db.query(Question).filter(Question.title == q_data["title"]).first()
                        if not question:
                            question = Question(
                                concept_id=concept.id,
                                title=q_data["title"],
                                difficulty=q_data["difficulty"],
                                source=q_data["source"],
                                url=q_data["url"],
                                estimated_solve_time=q_data.get("estimated_solve_time", 30),
                                is_important=q_data.get("is_important", False),
                                order_index=q_data["order_index"]
                            )
                            db.add(question)
                            db.flush()
                        else:
                            question.concept_id = concept.id
                            question.difficulty = q_data["difficulty"]
                            question.source = q_data["source"]
                            question.url = q_data["url"]
                            question.estimated_solve_time = q_data.get("estimated_solve_time", 30)
                            question.is_important = q_data.get("is_important", False)
                            question.order_index = q_data["order_index"]
                            db.add(question)
                            db.flush()

                        # Increment topic's total questions count
                        topic.total_questions += 1
                        db.add(topic)
                        db.flush()

                        # Bind Tags
                        for tag_name in q_data.get("tags", []):
                            tag = db.query(Tag).filter(Tag.name == tag_name).first()
                            if not tag:
                                tag = Tag(name=tag_name)
                                db.add(tag)
                                db.flush()
                            if tag not in question.tags:
                                question.tags.append(tag)

                        # Bind Companies
                        for comp_name in q_data.get("companies", []):
                            company = db.query(Company).filter(Company.name == comp_name).first()
                            if not company:
                                company = Company(name=comp_name)
                                db.add(company)
                                db.flush()
                            if company not in question.companies:
                                question.companies.append(company)
                        db.flush()

    db.commit()

    # 3. Resolve Topic Prerequisites
    for topic_slug, prereq_slugs in prerequisites_map.items():
        topic = db.query(Topic).filter(Topic.slug == topic_slug).first()
        if topic:
            for prereq_slug in prereq_slugs:
                prereq_topic = db.query(Topic).filter(Topic.slug == prereq_slug).first()
                if prereq_topic and prereq_topic not in topic.prerequisites:
                    topic.prerequisites.append(prereq_topic)
    db.commit()

    # 4. Create Default Admin User
    admin = db.query(User).filter(User.email == "admin@algopath.com").first()
    if not admin:
        admin = User(
            name="AlgoPath Admin",
            email="admin@algopath.com",
            hashed_password=get_password_hash("AdminPassword123!"),
            is_admin=True,
            streak_count=0
        )
        db.add(admin)
        db.commit()
        print("Default admin user created: admin@algopath.com / AdminPassword123!")
    else:
        print("Admin user already exists.")
