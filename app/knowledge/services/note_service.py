"""
Note Service

Service class for managing notes with CRUD operations.
Handles database interactions for note management with SQLAlchemy ORM.
"""

import logging
from datetime import datetime

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.database.models import NoteModel  # Assuming SQLAlchemy model exists
from app.knowledge.models.note import (
    Note,
    NoteCreate,
    NoteResponse,
    NoteSearchQuery,
    NoteSearchResponse,
    NoteUpdate,
)

logger = logging.getLogger(__name__)


class NoteService:
    """
    Service for managing notes with database operations.

    Provides async CRUD operations for notes including search,
    filtering, and relationship management with knowledge sources.
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize the note service.

        Args:
            db_session: Async SQLAlchemy database session
        """
        self.db_session = db_session

    async def create_note(self, note_data: NoteCreate, author_id: str | None = None) -> NoteResponse:
        """
        Create a new note.

        Args:
            note_data: Note creation data
            author_id: ID of the note author

        Returns:
            Created note response

        Raises:
            ValidationError: If note data is invalid
        """
        try:
            logger.info(f"Creating new note: {note_data.title}")

            # Create note model instance
            note_model = NoteModel(
                title=note_data.title,
                content=note_data.content,
                source_ids=note_data.source_ids or [],
                tags=note_data.tags or [],
                author_id=author_id,
                is_public=note_data.is_public,
                note_metadata=note_data.metadata or {},  # Map metadata to note_metadata
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            # Add to session and commit
            self.db_session.add(note_model)
            await self.db_session.commit()
            await self.db_session.refresh(note_model)

            # Convert to Pydantic model and return response
            note = self._model_to_pydantic(note_model)
            logger.info(f"Successfully created note with ID: {note.id}")

            return NoteResponse.from_note(note)

        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error creating note: {str(e)}")
            raise ValidationError(f"Failed to create note: {str(e)}") from e

    async def get_note(self, note_id: str, author_id: str | None = None) -> NoteResponse:
        """
        Get a note by ID.

        Args:
            note_id: ID of the note to retrieve
            author_id: Optional author ID for access control

        Returns:
            Note response

        Raises:
            NotFoundError: If note is not found or access denied
        """
        try:
            logger.debug(f"Retrieving note: {note_id}")

            # Build query with optional author filter
            query = select(NoteModel).where(NoteModel.id == note_id)

            # Apply access control
            if author_id:
                query = query.where(or_(NoteModel.author_id == author_id, NoteModel.is_public is True))
            else:
                # Only public notes if no author specified
                query = query.where(NoteModel.is_public is True)

            result = await self.db_session.execute(query)
            note_model = result.scalar_one_or_none()

            if not note_model:
                raise NotFoundError(f"Note with ID {note_id} not found")

            note = self._model_to_pydantic(note_model)
            return NoteResponse.from_note(note)

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving note {note_id}: {str(e)}")
            raise ValidationError(f"Failed to retrieve note: {str(e)}") from e

    async def update_note(self, note_id: str, note_data: NoteUpdate, author_id: str | None = None) -> NoteResponse:
        """
        Update an existing note.

        Args:
            note_id: ID of the note to update
            note_data: Note update data
            author_id: ID of the note author for access control

        Returns:
            Updated note response

        Raises:
            NotFoundError: If note is not found
            ValidationError: If update fails or access denied
        """
        try:
            logger.info(f"Updating note: {note_id}")

            # Find the note with author check
            query = select(NoteModel).where(NoteModel.id == note_id)
            if author_id:
                query = query.where(NoteModel.author_id == author_id)

            result = await self.db_session.execute(query)
            note_model = result.scalar_one_or_none()

            if not note_model:
                raise NotFoundError(f"Note with ID {note_id} not found or access denied")

            # Update fields that are provided
            update_data = {}
            if note_data.title is not None:
                update_data["title"] = note_data.title
            if note_data.content is not None:
                update_data["content"] = note_data.content
            if note_data.source_ids is not None:
                update_data["source_ids"] = note_data.source_ids
            if note_data.tags is not None:
                update_data["tags"] = note_data.tags
            if note_data.is_public is not None:
                update_data["is_public"] = note_data.is_public
            if note_data.metadata is not None:
                update_data["metadata"] = note_data.metadata

            # Always update the timestamp
            update_data["updated_at"] = datetime.utcnow()

            # Apply updates
            for field, value in update_data.items():
                setattr(note_model, field, value)

            await self.db_session.commit()
            await self.db_session.refresh(note_model)

            note = self._model_to_pydantic(note_model)
            logger.info(f"Successfully updated note: {note_id}")

            return NoteResponse.from_note(note)

        except NotFoundError:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error updating note {note_id}: {str(e)}")
            raise ValidationError(f"Failed to update note: {str(e)}") from e

    async def delete_note(self, note_id: str, author_id: str | None = None) -> bool:
        """
        Delete a note.

        Args:
            note_id: ID of the note to delete
            author_id: ID of the note author for access control

        Returns:
            True if note was deleted successfully

        Raises:
            NotFoundError: If note is not found
            ValidationError: If deletion fails or access denied
        """
        try:
            logger.info(f"Deleting note: {note_id}")

            # Build delete query with author check
            query = delete(NoteModel).where(NoteModel.id == note_id)
            if author_id:
                query = query.where(NoteModel.author_id == author_id)

            result = await self.db_session.execute(query)

            if result.rowcount == 0:
                raise NotFoundError(f"Note with ID {note_id} not found or access denied")

            await self.db_session.commit()
            logger.info(f"Successfully deleted note: {note_id}")

            return True

        except NotFoundError:
            raise
        except Exception as e:
            await self.db_session.rollback()
            logger.error(f"Error deleting note {note_id}: {str(e)}")
            raise ValidationError(f"Failed to delete note: {str(e)}") from e

    async def list_notes(
        self,
        author_id: str | None = None,
        include_public: bool = True,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[NoteResponse], int]:
        """
        List notes with pagination and filtering.

        Args:
            author_id: Optional author ID to filter by
            include_public: Whether to include public notes
            limit: Maximum number of notes to return
            offset: Number of notes to skip
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            Tuple of (notes list, total count)
        """
        try:
            logger.debug(f"Listing notes with limit={limit}, offset={offset}")

            # Build base query
            query = select(NoteModel)
            count_query = select(func.count(NoteModel.id))

            # Apply filters
            filters = []
            if author_id:
                if include_public:
                    # Author's notes + public notes from others
                    filters.append(
                        or_(
                            NoteModel.author_id == author_id,
                            NoteModel.is_public is True,
                        )
                    )
                else:
                    # Only author's notes
                    filters.append(NoteModel.author_id == author_id)
            elif include_public:
                # Only public notes
                filters.append(NoteModel.is_public is True)

            if filters:
                filter_condition = and_(*filters) if len(filters) > 1 else filters[0]
                query = query.where(filter_condition)
                count_query = count_query.where(filter_condition)

            # Apply sorting
            sort_column = getattr(NoteModel, sort_by, NoteModel.updated_at)
            if sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Execute queries
            result = await self.db_session.execute(query)
            count_result = await self.db_session.execute(count_query)

            note_models = result.scalars().all()
            total_count = count_result.scalar()

            # Convert to response models
            notes = [NoteResponse.from_note(self._model_to_pydantic(model)) for model in note_models]

            logger.debug(f"Retrieved {len(notes)} notes out of {total_count} total")
            return notes, total_count

        except Exception as e:
            logger.error(f"Error listing notes: {str(e)}")
            raise ValidationError(f"Failed to list notes: {str(e)}") from e

    async def search_notes(self, search_query: NoteSearchQuery, author_id: str | None = None) -> NoteSearchResponse:
        """
        Search notes with advanced filtering.

        Args:
            search_query: Search parameters
            author_id: Optional author ID for access control

        Returns:
            Search results with notes and metadata
        """
        try:
            logger.debug(f"Searching notes with query: {search_query.query}")

            # Build base query
            query = select(NoteModel)
            count_query = select(func.count(NoteModel.id))

            # Apply search filters
            filters = []

            # Text search in title and content
            if search_query.query:
                search_term = f"%{search_query.query}%"
                filters.append(
                    or_(
                        NoteModel.title.ilike(search_term),
                        NoteModel.content.ilike(search_term),
                    )
                )

            # Filter by tags
            if search_query.tags:
                # Assuming tags are stored as JSON array
                for tag in search_query.tags:
                    filters.append(NoteModel.tags.contains([tag]))

            # Filter by source IDs
            if search_query.source_ids:
                for source_id in search_query.source_ids:
                    filters.append(NoteModel.source_ids.contains([source_id]))

            # Filter by author
            if search_query.author_id:
                filters.append(NoteModel.author_id == search_query.author_id)
            elif author_id:
                # Apply access control
                filters.append(or_(NoteModel.author_id == author_id, NoteModel.is_public is True))

            # Filter by public status
            if search_query.is_public is not None:
                filters.append(NoteModel.is_public == search_query.is_public)

            # Date filters
            if search_query.created_after:
                filters.append(NoteModel.created_at >= search_query.created_after)

            if search_query.created_before:
                filters.append(NoteModel.created_at <= search_query.created_before)

            # Apply all filters
            if filters:
                filter_condition = and_(*filters)
                query = query.where(filter_condition)
                count_query = count_query.where(filter_condition)

            # Apply sorting
            sort_column = getattr(NoteModel, search_query.sort_by, NoteModel.updated_at)
            if search_query.sort_order.lower() == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())

            # Apply pagination
            query = query.offset(search_query.offset).limit(search_query.limit)

            # Execute queries
            result = await self.db_session.execute(query)
            count_result = await self.db_session.execute(count_query)

            note_models = result.scalars().all()
            total_count = count_result.scalar()

            # Convert to response models
            notes = [NoteResponse.from_note(self._model_to_pydantic(model)) for model in note_models]

            has_more = (search_query.offset + len(notes)) < total_count

            logger.info(f"Search found {total_count} notes, returning {len(notes)}")

            return NoteSearchResponse(
                notes=notes,
                total=total_count,
                limit=search_query.limit,
                offset=search_query.offset,
                has_more=has_more,
            )

        except Exception as e:
            logger.error(f"Error searching notes: {str(e)}")
            raise ValidationError(f"Failed to search notes: {str(e)}") from e

    async def get_notes_by_source(
        self,
        source_id: str,
        author_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NoteResponse], int]:
        """
        Get notes that reference a specific knowledge source.

        Args:
            source_id: ID of the knowledge source
            author_id: Optional author ID for access control
            limit: Maximum number of notes to return
            offset: Number of notes to skip

        Returns:
            Tuple of (notes list, total count)
        """
        try:
            logger.debug(f"Getting notes for source: {source_id}")

            # Build query for notes containing the source ID
            query = select(NoteModel).where(NoteModel.source_ids.contains([source_id]))
            count_query = select(func.count(NoteModel.id)).where(NoteModel.source_ids.contains([source_id]))

            # Apply access control
            if author_id:
                access_filter = or_(NoteModel.author_id == author_id, NoteModel.is_public is True)
                query = query.where(access_filter)
                count_query = count_query.where(access_filter)
            else:
                query = query.where(NoteModel.is_public is True)
                count_query = count_query.where(NoteModel.is_public is True)

            # Apply pagination and sorting
            query = query.order_by(NoteModel.updated_at.desc()).offset(offset).limit(limit)

            # Execute queries
            result = await self.db_session.execute(query)
            count_result = await self.db_session.execute(count_query)

            note_models = result.scalars().all()
            total_count = count_result.scalar()

            # Convert to response models
            notes = [NoteResponse.from_note(self._model_to_pydantic(model)) for model in note_models]

            return notes, total_count

        except Exception as e:
            logger.error(f"Error getting notes by source {source_id}: {str(e)}")
            raise ValidationError(f"Failed to get notes by source: {str(e)}") from e

    def _model_to_pydantic(self, note_model: NoteModel) -> Note:
        """
        Convert SQLAlchemy model to Pydantic model.

        Args:
            note_model: SQLAlchemy note model instance

        Returns:
            Pydantic Note model
        """
        return Note(
            id=note_model.id,
            title=note_model.title,
            content=note_model.content,
            source_ids=note_model.source_ids,
            tags=note_model.tags,
            author_id=note_model.author_id,
            is_public=note_model.is_public,
            metadata=note_model.note_metadata,  # Map note_metadata back to metadata
            created_at=note_model.created_at,
            updated_at=note_model.updated_at,
        )
