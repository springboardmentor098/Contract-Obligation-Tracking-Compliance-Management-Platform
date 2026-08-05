from pydantic_settings import BaseSettings

<<<<<<< HEAD
=======

>>>>>>> cb87ace116b09ed98d5d64392b80a596edfa80ce
class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

<<<<<<< HEAD
settings = Settings()
=======

settings = Settings()
>>>>>>> cb87ace116b09ed98d5d64392b80a596edfa80ce
