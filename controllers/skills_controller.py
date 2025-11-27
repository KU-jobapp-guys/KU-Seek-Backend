"""Controller for Tags and Terms endpoints."""

from typing import List, Dict
from swagger_server.openapi_server import models
from logger.custom_logger import get_logger
from .models.tag_term_model import Tags, Terms
from .decorators import login_required, role_required, rate_limit

logger = get_logger()


class SkillsController:
    """Controller for handling tags and terms retrieval."""

    def __init__(self, database):
        """Initialize with a database instance."""
        self.db = database

    @login_required
    @rate_limit
    def get_tag(self, tag_id: int) -> Dict:
        """Return a tag by its id.

        Raises ValueError if not found.
        """
        session = self.db.get_session()
        try:
            tag = session.query(Tags).where(Tags.id == tag_id).one_or_none()
            if not tag:
                logger.warning("Tag not found: %s", tag_id)
                return models.ErrorMessage("Tag not found"), 404

            return {"id": tag.id, "name": tag.name}
        except Exception:
            session.rollback()
            logger.exception("Database error fetching tag %s", tag_id)
            return models.ErrorMessage("Database error"), 500
        finally:
            session.close()

    @login_required
    @rate_limit
    def get_term(self, term_id: int) -> Dict:
        """Return a term by its id.

        Raises ValueError if not found.
        """
        session = self.db.get_session()
        try:
            term = session.query(Terms).where(Terms.id == term_id).one_or_none()
            if not term:
                logger.warning("Term not found: %s", term_id)
                return models.ErrorMessage("Term not found"), 404

            return {"id": term.id, "name": term.name, "type": term.type}
        except Exception:
            session.rollback()
            logger.exception("Database error fetching term %s", term_id)
            return models.ErrorMessage("Database error"), 500
        finally:
            session.close()

    @login_required
    @rate_limit
    def get_terms(self) -> List[Dict]:
        """Return all terms (id, name, type)."""
        session = self.db.get_session()
        try:
            terms = session.query(Terms).all()
            return [{"id": t.id, "name": t.name, "type": t.type} for t in terms]
        except Exception:
            session.rollback()
            logger.exception("Database error fetching terms")
            return models.ErrorMessage("Database error"), 500
        finally:
            session.close()

    @role_required(["Company"])
    def get_tags(self) -> List[str]:
        """Return all tag names (used as workFields)."""
        session = self.db.get_session()
        try:
            tags = session.query(Tags).all()
            return [t.name for t in tags]
        except Exception:
            session.rollback()
            logger.exception("Database error fetching tags")
            return models.ErrorMessage("Database error"), 500
        finally:
            session.close()

    @role_required(["Company"])
    @rate_limit
    def post_tag(self, name: str) -> tuple:
        """Create a tag if it doesn't exist, otherwise return existing id.

        Returns the id of the tag (new or existing).
        """
        if not name or not isinstance(name, str):
            logger.warning("Invalid tag name provided: %s", name)
            return models.ErrorMessage("Invalid tag name"), 400

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
        except Exception:
            session.rollback()
            logger.exception("Database error creating tag %s", name)
            return models.ErrorMessage("Database error"), 500
        finally:
            session.close()
