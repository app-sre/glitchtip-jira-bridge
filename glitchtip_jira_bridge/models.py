from pydantic import BaseModel


class Field(BaseModel):
    title: str
    value: str
    short: bool


class Attachment(BaseModel):
    title: str
    title_link: str
    text: str
    image_url: str | None = None
    color: str | None = None
    fields: list[Field] | None = None
    mrkdown_in: list[str] | None = None


class GlitchtipAlert(BaseModel):
    alias: str
    text: str
    attachments: list[Attachment]
    # pydantic config
    model_config = {"extra": "ignore"}

    @property
    def labels(self) -> list[str]:
        l: list[str] = []
        for a in self.attachments:
            for f in a.fields or []:
                match f.title.lower():
                    case "project":
                        l.append(f"project:{f.value}")
                    case "release":
                        l.append(f"release:{f.value}")
                    case "environment":
                        l.append(f"environment:{f.value}")
                    case _:
                        pass
        return l

    @property
    def issue_title(self) -> str:
        return self.attachments[0].title

    @property
    def issue_url(self) -> str:
        return self.attachments[0].title_link

    @property
    def issue_text(self) -> str:
        return self.attachments[0].text


class Issue(BaseModel):
    jira_key: str
    glitchtip_issue_url: str
