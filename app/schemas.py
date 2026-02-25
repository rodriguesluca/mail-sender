from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union


class EmailRequest(BaseModel):
    to_email: Union[EmailStr, List[EmailStr]]
    cc_email: Optional[Union[EmailStr, List[EmailStr]]] = None
    subject: str
    body: str
    smtp_user: str
    smtp_password: str
    smtp_host: str = "smtp.office365.com"
    smtp_port: int = 587
    smtp_tls: bool = True
    attachment_base64: Optional[str] = None
    attachment_filename: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "to_email": [
                        "example@digitaly.tech",
                        "example2@digitaly.tech",
                    ],
                    "cc_email": ["example3@mail.com"],
                    "subject": "Transcrição Dom Eurico",
                    "body": "Transcrição Dom Eurico Concluida.\nEssa é uma mensagem automática\n",
                    "smtp_user": "seu.email@seuemail.com",
                    "smtp_password": "senha criptografada",
                    "smtp_host": "smtp.office365.com",
                    "smtp_port": 587,
                    "smtp_tls": True,
                    "attachment_base64": "",
                    "attachment_filename": "teste_dom_eurico.xlsx",
                }
            ]
        }
    }


class EncryptRequest(BaseModel):
    raw_password: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"raw_password": "my_super_secret_password"}]
        }
    }
