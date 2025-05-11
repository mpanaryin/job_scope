import abc

from src.vacancies.domain.interfaces.vacancy_repo import IVacancyRepository


class IVacancyUnitOfWork(abc.ABC):
    """
    Unit of Work pattern interface for transactional operations on vacancies.

    Provides scoped access to a vacancy repository and ensures consistency
    through commit/rollback semantics.
    """

    vacancies: IVacancyRepository

    async def __aenter__(self):
        """
        Enter the Unit of Work context.

        :return: Self with initialized transactional context.
        """
        return self

    async def __aexit__(self, *args):
        """
        Exit the Unit of Work context and perform rollback if not committed.
        """
        await self.rollback()

    async def commit(self):
        """
        Commit all changes made during the unit of work.
        """
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        """
        Persist all changes to the database.
        """
        pass

    @abc.abstractmethod
    async def rollback(self):
        """
        Revert all changes made during the unit of work.
        """
        pass
