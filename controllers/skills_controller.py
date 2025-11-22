"""Controller for Tags and Terms endpoints."""

from typing import List, Dict
from connexion.exceptions import ProblemException
from .models.tag_term_model import Tags, Terms
from .decorators import login_required, role_required


class SkillsController:
    """Controller for handling tags and terms retrieval."""

    def __init__(self, database):
        """Initialize with a database instance."""
        self.db = database

    @login_required
    def get_tag(self, tag_id: int) -> Dict:
        """Return a tag by its id.

        Raises ValueError if not found.
        """
        session = self.db.get_session()
        try:
            tag = session.query(Tags).where(Tags.id == tag_id).one_or_none()
            if not tag:
                raise ValueError("Tag not found")

            return {"id": tag.id, "name": tag.name}
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    @login_required
    def get_term(self, term_id: int) -> Dict:
        """Return a term by its id.

        Raises ValueError if not found.
        """
        session = self.db.get_session()
        try:
            term = session.query(Terms).where(Terms.id == term_id).one_or_none()
            if not term:
                raise ValueError("Term not found")

            return {"id": term.id, "name": term.name, "type": term.type}
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    @login_required
    def get_terms(self) -> List[Dict]:
        """Return all terms (id, name, type)."""
        session = self.db.get_session()
        try:
            terms = session.query(Terms).all()
            return [{"id": t.id, "name": t.name, "type": t.type} for t in terms]
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    @role_required(["Company"])
    def get_tags(self) -> List[str]:
        """Return all tag names (used as workFields)."""
        session = self.db.get_session()
        try:
            tags = session.query(Tags).all()
            return [t.name for t in tags]
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()

    @role_required(["Company"])
    def post_tag(self, name: str) -> tuple:
        """Create a tag if it doesn't exist, otherwise return existing id.

        Returns the id of the tag (new or existing).
        """
        if not name or not isinstance(name, str):
            raise ValueError("Invalid tag name")

        session = self.db.get_session()
        try:
            existing = session.query(Tags).where(Tags.name == name).one_or_none()
            if existing:
                return existing.id, False

            tag = Tags(name=name)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag.id, True
        except Exception as e:
            session.rollback()
            raise ProblemException(f"Database Error {str(e)}")
        finally:
            session.close()
