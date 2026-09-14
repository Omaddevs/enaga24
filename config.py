from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str
    admin_ids: str = ""
    db_path: str = "data/enaga24.db"

    @property
    def admins(self) -> list[int]:
        result: list[int] = []
        for part in self.admin_ids.split(","):
            part = part.strip()
            if part.isdigit() or (part.startswith("-") and part[1:].isdigit()):
                result.append(int(part))
        return result


settings = Settings()
