import os
import json
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db

app = create_app()


@app.cli.command('seed-db')
def seed_db():
    """Seed questions and remedies from seed_data/ JSON files."""
    with app.app_context():
        _seed_questions()
        _seed_remedies()
        print("Database seeded successfully.")


def _seed_questions():
    from app.models.question import Question
    if Question.query.count() > 0:
        print("Questions already seeded — skipping.")
        return
    path = os.path.join(os.path.dirname(__file__), 'seed_data', 'questions.json')
    with open(path, 'r') as f:
        questions = json.load(f)
    for q in questions:
        db.session.add(Question(**q))
    db.session.commit()
    print(f"Seeded {len(questions)} questions.")


def _seed_remedies():
    from app.models.remedy import Remedy, ConditionRemedy
    if Remedy.query.count() > 0:
        print("Remedies already seeded — skipping.")
        return
    path = os.path.join(os.path.dirname(__file__), 'seed_data', 'remedies.json')
    with open(path, 'r') as f:
        data = json.load(f)

    id_map = {}
    for r in data['remedies']:
        remedy = Remedy(
            name=r['name'],
            ingredients=r.get('ingredients', []),
            instructions=r['instructions'],
            confidence_level=r.get('confidence_level', 'High'),
            source_url=r.get('source_url'),
            lifestyle_tags=r.get('lifestyle_tags', []),
        )
        db.session.add(remedy)
        db.session.flush()
        id_map[r['key']] = remedy.id

    for mapping in data['condition_remedies']:
        db.session.add(ConditionRemedy(
            final_condition=mapping['final_condition'],
            remedy_id=id_map[mapping['remedy_key']],
            sort_order=mapping.get('sort_order', 0),
        ))
    db.session.commit()
    print(f"Seeded {len(data['remedies'])} remedies and {len(data['condition_remedies'])} condition mappings.")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
