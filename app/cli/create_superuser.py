import asyncio

import typer
from pydantic import ValidationError

from ..core.settings import settings
from ..core.security import PasswordHasher
from ..db import async_session_factory, UnitOfWork
from ..exceptions import ConflictException
from ..schemas import SuperUserRequest
from ..services import UserService

app = typer.Typer()


@app.command()
def create_superuser():
    async def _run():
        try:
            superuser_data = SuperUserRequest(
                email=settings.superuser.EMAIL,
                password=settings.superuser.PASSWORD,
                name=settings.superuser.NAME,
                surname=settings.superuser.SURNAME,
                gender=settings.superuser.GENDER,
                phone=settings.superuser.PHONE,
            )
        except ValidationError as err:
            typer.secho(f"Invalid superuser config: {err}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

        async with async_session_factory() as session:
            async with UnitOfWork(session) as uow:
                service = UserService(uow=uow, security=PasswordHasher())
                try:
                    superuser = await service.create_user(superuser_data)
                except ConflictException:
                    raise typer.Exit(code=0)
                except Exception as err:
                    typer.secho(f"Unexpected error: {err}", fg=typer.colors.RED)
                    raise typer.Exit(code=1)
                else:
                    typer.secho(
                        f"Superuser created: {superuser.email}", fg=typer.colors.GREEN
                    )

    asyncio.run(_run())


if __name__ == "__main__":
    app()
